import argparse
import re
import tempfile
from pathlib import Path

import torch
from rich.console import Console
from rich.live import Live
from rich.progress import Progress
from rich.table import Table
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from GhidraBridge.ghidra_bridge import GhidraBridge

class Monocle:
    def _load_model(self, model_name, device):
        """
        Load the pre-trained language model and tokenizer.

        Args:
            model_name (str): Name of the pre-trained model.
            device (str): Device to load the model onto.

        Returns:
            model (transformers.PreTrainedModel): Loaded language model.
            tokenizer (transformers.PreTrainedTokenizer): Loaded tokenizer.
        """
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2", quantization_config=quantization_config)
        tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
        return model, tokenizer
    
    def _get_code_from_decom_file(self, path_to_file):
        """
        Read and return the code from a decom file.

        Args:
            path_to_file (str): Path to the decom file.

        Returns:
            str: Content of the decom file.
        """
        with open(path_to_file, "r") as file:
            return file.read()
        
    def _decompile_binary(self, decom_folder, binary):
        """
        Decompile the binary file and extract function information.

        Args:
            decom_folder (str): Folder to store decompiled files.
            binary (str): Path to the binary file.

        Returns:
            list: List of dictionaries containing binary name, function name, and code.
        """
        g_bridge = GhidraBridge()
        g_bridge.decompile_binaries_functions(binary, decom_folder)
        
        list_of_decom_files = []

        for file_path in Path(decom_folder).iterdir():
            binary_name, function_name, *_ = Path(file_path).name.split("__")
            list_of_decom_files.append({"binary_name": binary_name, "function_name": function_name, "code": self._get_code_from_decom_file(file_path)})

        return list_of_decom_files
        
    def _generate_dialogue_response(self, model, tokenizer, device, messages):
        """
        Generate response from the language model given the input messages.

        Args:
            model (transformers.PreTrainedModel): Loaded language model.
            tokenizer (transformers.PreTrainedTokenizer): Loaded tokenizer.
            device (str): Device to run the model on.
            messages (list): List of input messages.

        Returns:
            str: Generated response.
        """
        encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")
        model_inputs = encodeds.to(device)
        generated_ids = model.generate(model_inputs, max_new_tokens=200, do_sample=False, pad_token_id=50256)
        decoded = tokenizer.batch_decode(generated_ids, skip_special_tokens=False)
        return decoded[0]

    def _generate_table_row(self, binary_name="", function_name="", score=0, explanation=0):
        """
        Generate a row for the result table.

        Args:
            binary_name (str): Name of the binary file.
            function_name (str): Name of the function.
            score (int): Score assigned to the function.
            explanation (str): Explanation of the score.

        Returns:
            dict: Dictionary representing the table row.
        """
        return {
            "binary_name": str(binary_name),
            "function_name": function_name,
            "score": str(score),
            "explanation": str(explanation),
        }

    def _generate_table(self, rows, title=None):
        """
        Generate a table from the given rows.

        Args:
            rows (list): List of dictionaries representing table rows.
            title (str, optional): Title of the table. Defaults to None.

        Returns:
            rich.table.Table: Generated table.
        """
        table = Table()

        for column_name in rows[0].keys():
            table.add_column(str(column_name).upper().replace("_", " "))

        for row_dict in rows:
            table.add_row(*row_dict.values())

        table.caption = "Monocle"

        if title:
            formatted_title = " ".join(word.capitalize() for word in title.split())
            table.title = f"[red bold underline]{formatted_title}[/red bold underline]"

        return table

    def _get_args(self):
        """
        Parse command line arguments.

        Returns:
            argparse.Namespace: Parsed arguments.
        """
        parser = argparse.ArgumentParser(description="Local Language Model (LLM) - Explain code snippets")
        parser.add_argument("--binary", "-b", required=True, help="The Binary to search")
        parser.add_argument("--find", "-f", required=True, help="The component to find")
        return parser.parse_args()
    
    def _remove_inst_tags(self, text):
        """
        Remove instruction tags from the given text.

        Args:
            text (str): Input text containing instruction tags.

        Returns:
            str: Text with instruction tags removed.
        """
        pattern = r'\[INST\].*?\[/INST\]'
        clean_text = re.sub(pattern, '', text, flags=re.DOTALL)
        return clean_text.replace("<s>", "").replace("</s>", "").replace("Explanation:", "").strip()

    def entry(self):
        """
        Entry point of the program.
        """
        args = self._get_args()
        console = Console()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model_name = "mistralai/Mistral-7B-Instruct-v0.1"
        model, tokenizer = self._load_model(model_name, device)
        console.clear()
        
        list_of_decom_files = []
        with tempfile.TemporaryDirectory() as tmpdirname:
            with console.status("[bold green]Decompiling binary...") as status:
                list_of_decom_files = self._decompile_binary(tmpdirname, args.binary)
                # Spinner will stop spinning after the task is finished
                console.print("[bold green]Processing finished!")

                console.clear()

            with Live(Table(), refresh_per_second=4, console=console) as live:
                rows = []    

                for function in list_of_decom_files:
                    binary_name = function["binary_name"]
                    function_name = function["function_name"]
                    code = function["code"]

                    question = f"You have been asked to review C decompiled code from Ghidra and identify the following '{args.find}'. Return a score between 0 and 10, where 0 means there is no indication, 1 to 2 means there is something related, 3 to 4 means there is a degree of evidence, 5 to 6 means that there is more evidence, and 7 to 10 means there is significant evidence. You should be certain that the code meets these scores. Format your response as a single number score, followed my a new line, followed by your explanation. \n Code: \n {code.strip()}"
                    
                    result = self._generate_dialogue_response(model, tokenizer, device, [{"role": "user", "content": question}])
                    result = self._remove_inst_tags(result)

                    ans_number, *explanation = result.split("\n")
                    explanation = "".join(explanation)

                    if int(ans_number) == 0:
                        explanation = ""

                    rows.append(self._generate_table_row(binary_name=binary_name, function_name=function_name, score=ans_number, explanation=explanation))

                    for row_dict in rows:
                        words_to_replace = ["[green]", "[orange1]", "[red]"]
                        score_value = row_dict["score"]
                        for word in words_to_replace:
                            score_value = score_value.replace(word, "")
                        row_dict["score"] = score_value

                    rows.sort(key=lambda x: int(x['score']), reverse=True)
                    
                    max_score = int(max(rows, key=lambda x: int(x['score']))['score'])
                    for row in rows:
                        score = int(row['score'])
                        if score >= max_score * 0.75:
                            row['score'] = f"[green]{score}"
                        elif score >= max_score * 0.5:
                            row['score'] = f"[orange1]{score}"
                        else:
                            row['score'] = f"[red]{score}"
                    
                    console.clear()
                    live.update(self._generate_table(rows, args.find))

def run():
    finder = Monocle()
    finder.entry()

if __name__ == "__main__":
    run()

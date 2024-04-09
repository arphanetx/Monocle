import concurrent
import hashlib
import shutil
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from tqdm import tqdm


class GhidraBridge():
    def __init__(self):
        pass

    def _execute_blocking_command(self, command_as_list):
        if command_as_list != None:
            #print("Executing command: {}".format(command_as_list))
            result = subprocess.run(command_as_list, capture_output=False, stdout=subprocess.PIPE)
            return result

    def generate_ghidra_decom_script(self, path_to_save_decoms_to, file_to_save_script_to):

        script = """# SaveFunctions.py
        
# Import necessary Ghidra modules
from ghidra.program.model.listing import Function
from ghidra.util.task import TaskMonitor
from ghidra.app.decompiler import DecompInterface
import os
import time
import re

# Function to save the decompiled C code of a function to a file
def save_function_c_code(function, output_directory):
    function_name = function.getName()
    function_c_code = decompile_function_to_c_code(function)
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Save the C code to a file
    current_epoch_time = int(time.time())

    # Combine the elements to create the file path
    output_file_path = os.path.join(
        output_directory,
        re.sub(r'[^\w\-\.\\/]', '_', "{}__{}__{}.c".format(
            function.getProgram().getName(),
            function_name,
            int(time.time())
        ))
    )

    with open(output_file_path, 'w') as output_file:
        output_file.write(function_c_code)

# Function to decompile a function to C code
def decompile_function_to_c_code(function):
    decompiler = get_decompiler(function.getProgram())
    result = decompiler.decompileFunction(function, 0, TaskMonitor.DUMMY)
    return result.getDecompiledFunction().getC()

# Function to get the decompiler for the current program
def get_decompiler(program):
    decompiler_options = program.getOptions("Decompiler")
    decompiler_id = decompiler_options.getString("decompiler", "ghidra")
    decompiler = DecompInterface()
    decompiler.openProgram(program)
    return decompiler

# Main function to iterate through all functions and save their C code
def save_all_functions_to_files():
    current_program = getCurrentProgram()
    listing = current_program.getListing()
    
    # Specify the output directory
    output_directory = r"<PATH>"
    
    # Iterate through all functions
    for function in listing.getFunctions(True):
        function_name = function.getName()
        save_function_c_code(function, output_directory)

# Run the main function
save_all_functions_to_files()
        """.replace("<PATH>", path_to_save_decoms_to)

        with open(file_to_save_script_to, "w") as file:
            file.write(script)

    def _check_if_ghidra_project_exists(self, project_folder, project_name):

        project_folder_path = Path(project_folder, project_name + ".gpr")

        return project_folder_path.exists()

    def _construct_ghidra_headless_command(self, binary_path, script_path, binary_hash,
                                           ghidra_project_dir=Path.cwd().name):

        binary_name = "analyzeHeadless.bat"

        # Check if the binary is on the PATH
        headless = shutil.which(binary_name)

        temp_script_path = Path(script_path)
        temp_script_dir = temp_script_path.parent
        Path(temp_script_dir).resolve()
        if headless is not None:
            pass#print(f"{binary_name} found at: {headless}")
        else:
            # Binary not found, prompt user to provide the path
            user_provided_path = input(f"{binary_name} not found on the PATH. Please provide the full path: ")

            # Verify if the provided path is valid
            if shutil.which(user_provided_path) is not None:
                headless = user_provided_path
                print(f"{binary_name} found at: {headless}")

                headless = user_provided_path
            else:
                raise Exception(f"Error: {binary_name} not found at the provided path.")

        with tempfile.TemporaryDirectory() as ghidra_project_dir:
            # Construct Ghidra headless command
            commandStr = [
                headless,
                ghidra_project_dir,
                binary_hash,
                "-import",
                binary_path,
                "-scriptPath",
                temp_script_dir,
                "-postScript",
                temp_script_path.name
            ]

            # Run Ghidra headless command
            self._execute_blocking_command(commandStr)

    def _hash_binary(self, binary_path):
        with open(binary_path, 'rb') as f:
            binary_hash = hashlib.sha256(f.read()).hexdigest()
        return binary_hash

    def decompile_binaries_functions(self, path_to_binary, decom_folder):
        binary_hash = self._hash_binary(path_to_binary)
        with tempfile.TemporaryDirectory() as tmpdirname:
            script_path = Path(tmpdirname, "decom_script.py").resolve()
            self.generate_ghidra_decom_script(decom_folder, script_path)
            self._construct_ghidra_headless_command(path_to_binary, script_path, binary_hash)

    def decompile_all_binaries_in_folder(self, path_to_folder, decom_folder):
        # Create a list to store all the file paths
        files_to_process = [file_path for file_path in Path(path_to_folder).iterdir() if file_path.is_file()]

        # Use a ProcessPoolExecutor to execute the decompilation in parallel
        with ProcessPoolExecutor() as executor:
            # Create a list of futures
            futures = [executor.submit(self.decompile_binaries_functions, file_path, decom_folder) for file_path in
                       files_to_process]

            # Use tqdm to show progress
            for _ in tqdm(concurrent.futures.as_completed(futures), total=len(files_to_process),
                          desc="Decompiling functions in binaries from {}".format(path_to_folder)):
                pass


if __name__ == '__main__':
    raise Exception("This is not a program entrypoint!")


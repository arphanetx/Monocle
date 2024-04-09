<p align="center">
    <img width=100% src="logo.png">
  </a>
</p>
<p align="center"> 🤖 Large Language Model For Binary Analysis Search ⚙️ </b> </p>

<div align="center">

![GitHub contributors](https://img.shields.io/github/contributors/yourusername/Monocle)
![GitHub Repo stars](https://img.shields.io/github/stars/yourusername/Monocle?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/yourusername/Monocle?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/Monocle)
<br>

</div>

Monocle is a large language model designed specifically for binary analysis search. Monocle can be provided with a binary and a search criteria (e.g. authentication code, vulnerable code, password strings, and more) and it will decompile the binary and use it's in-built LLM to identify and score areas of the code that meet the criteria. 
* **🔬 Binary Search:** Without any prior knowledge Monocle will support in answering binary analysis questions related to the target.
* **🤖 Plain text and open ended questions:** As Monocle is backed by an LLM, queries passed to it are written in plain text.
* **🛠️ Ghidra Enabled:** Monocle uses Ghidra headless to enable decompilation of functions!

# ⚙️ Setup

## System Requirements
Monocle uses the Mistral-7B-Instruct-v0.2 model, and where possible offloads processing to your systems GPU. It is reccomended to run Monocle on a machine with 32GB of RAM and a dedicated Nvidia GPU with atleast 4GB of memory. **However** it can run on lower spec machines, but will be significantly slower.

## Dependencies

Monocle requires [Ghidra](https://ghidra-sre.org/) to be installed and accessible. Additionally, ensure that `analyzeHeadless` is available in your environment. 

Python dependencies can be found in `requirements.txt` file:

```
pip install -r requirements.txt
```

Monocle can then be installed using the ```./setup.py``` script as below:

```
./setup.py install
```

**Optionally** If your machine supports it, you may want to install Nvidia Cuda of which will greatly increase the speed and optimisation of the used model. A [guide here](https://telin.ugent.be/telin-docs/windows/pytorch/) can be seen on how to setup Cuda.

## Running

To utilize Monocle, follow the instructions below:

### Binary Search
Execute Monocle with the appropriate parameters to conduct binary search tasks.

```bash
python3 monocle.py --binary <path-to-binary> --find <component-to-find>
```

# Mistral-7B-Instruct-v0.2
Behind the scenes Monocle uses the ```Mistral-7B-Instruct-v0.2``` model. The Mistral-7B-Instruct-v0.2 Large Language Model (LLM) is an instruct fine-tuned version of the Mistral-7B-v0.2. More can be found on the model [here!](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2).

# 🙏 Contributions

Monocle is an open-source project and welcomes contributions from the community. If you would like to contribute to
Monocle, please follow these guidelines:

- Fork the repository to your own GitHub account.
- Create a new branch with a descriptive name for your contribution.
- Make your changes and test them thoroughly.
- Submit a pull request to the main repository, including a detailed description of your changes and any relevant
  documentation.
- Wait for feedback from the maintainers and address any comments or suggestions (if any).
- Once your changes have been reviewed and approved, they will be merged into the main repository.

# ⚖️ Code of Conduct

Monocle follows the Contributor Covenant Code of Conduct. Please make sure to review and adhere to this code of conduct when contributing to Monocle.

# 🐛 Bug Reports and Feature Requests

If you encounter a bug or have a suggestion for a new feature, please open an issue in the GitHub repository. Please provide as much detail as possible, including steps to reproduce the issue or a clear description of the proposed feature. Your feedback is valuable and will help improve Monocle for everyone.

# 📜 License

[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)

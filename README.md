# Monalisa : a reconstruction tool-box for non-cartesian and cartesian MRI data

This repository contains code for performing MRI reconstruction with non-cartesian or cartesian data.
Several iterative reconstruction are implemented. They all consist in minimizing a regularized or non-regularized least-square objective function. 

Make sure to **visit our [documentation](https://mattechlab.github.io/monalisa/)**.

If you find this useful, **please leave us a star!**

## Usage and installation

To get started with the MRI reconstruction code, follow these steps:

1. Clone the repository

```sh
   git clone https://github.com/MattechLab/monalisa.git
   cd monalisa
```

2. Great, installation is done! You are now ready to run the first [tutorial](https://mattechlab.github.io/monalisa/3-1_example1.html)


## Getting started

For better installation guidelines and much more **check Monalisa's documentation** [here](https://mattechlab.github.io/monalisa/)!

## Navigating This Repository

This repository is organized into 5 main subfolders, each with a specific purpose:

- **`demo/`** – Example scripts and tutorials demonstrating how to use the toolbox.

- **`docs/`** – Documentation sources and build tools for generating the project’s documentation.

- **`src/`** – Core source code of the Monalisa toolbox. This is where the main functionality is implemented.

- **`third_part/`** – Third-party software dependencies (some with local modifications). These are distributed under licenses different from Monalisa’s.

- **`tests/`** – Unit tests and validation scripts to ensure code reliability.


## Convert MATLAB code to Python (agentic pipeline)

Use an IDE agent (Claude code, Codex, Cursor, etc):
1. Prompt to tha agent : 
```
"Load porting/prompts/system_ide_agent.md as your system prompt, then run:
python porting/scripts/build_agent_context.py"
```

Use the deterministic-first porting framework under `porting/`.

1. Run full workflow on all files:
```bash
python porting/scripts/run_agentic_porting_workflow.py `  --roots src,demo,tests,third_part `  --force --overwrite-manual `  --model granite3.2:8b `  --fallback-model gpt-oss:20b `  --auto-pull-model `  --max-iterations 3 `  --max-files-per-iteration 20 `  --stream-repair-logs `  --llm-timeout-seconds 180 `  --dynamic-llm-timeout `  --dynamic-timeout-base-seconds 45 `  --dynamic-timeout-per-line-seconds 3 `  --dynamic-timeout-min-seconds 60 `  --dynamic-timeout-max-seconds 900 `  --enable-matlab-help `  --matlab-help-max-functions 1 `  --matlab-help-timeout-seconds 20
```

2. Cleanup artifacts when needed:
```bash
python porting/scripts/cleanup_pipeline_artifacts.py --clean-cache --prune-stale-tests --remove-empty-dirs --apply
```

See detailed instructions in `porting/README.md`.


## Project logic 

When we pull upstream, we do all the tests we can do, we analize the project structure, we make a function call graph and from the leaves, we extract the core logic of each file and writting it to a .txt file with every information we can put like the argument (global/local), the functions (name, arguments, etc...), import/dependencies, etc... 
We can the compare the file with the previous one and add/remove/update the necessary part to each code 
The script will do everything automatically (implement and report what he did for the agent to write more clearly)
There will be a script for any part of the porting (the goal is to not relly on the agent one day), get_project_structure, extract_core_logic, compare_logic, update_file, etc...

### Porting logic
- The script that extract the function_call_graph is executed and will output 'function_call_graph.txt' or .json
- Execute search_new_matlab_files.py to produce a file 'matlab_files.txt' that contains all the matlab files
- Execute the script that extract the logic of the matlab code and produce 'extracted_logic.json' based on 'matlab_files.txt'
- The script that compares the logic of the old matlab code and new matlab code is executed and produce 'difference_old_new_logic.json' based on 'matlab_files.txt'
- The script that compares the logic of the matlab code and the python code is executed and produce difference_matlab_python_logic.json
- Based on its output, the script that will chose the order of porting will be executed, to port the file/function that have no dependencies to other file/function first. (the goal is to isolated for the tests)
- We port one file/function from matlab to python
- We execute the tests (if any) for the function/file -> if it doesn't pass, we reiterate the previous steps with different argument ; if pass, we write docs of what changed and we go to next function/file
- Same thing for the loss functions (compare to matlab result) if it exceeds a certain threshold



## Help us improve

Monalisa is still very young. If you encounter an issue, please consider **opening a GitHub issue** in the repository. If you know how to fix the problem, feel free to submit a pull request!

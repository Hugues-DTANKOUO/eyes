# Installing and using Poetry in this project

## Installing Poetry

Please refer to [the official documentation](https://python-poetry.org/docs/)

Otherwise, here's a quick guide:

### Make sure you have `python 3.11` on your machine
- Execute the command:
```shell
python --version
```
- Or on Linux and Mac, the command:
```shell
python3 --version
```
### Install `pipx` [(official documentation)](https://pipx.pypa.io/stable/installation/)

- Execute the following command (on Linux or Mac, replace `python` with `python3`):
```shell
python -m pip install pipx
```
- Verify that the Python scripts path is added to your PATH environment variable:
```shell
python -m pipx ensurepath
```
- Restart your terminal

- Verify that `pipx` installation was successful with the command:
```shell
pipx --version
```

### Install `Poetry`
- Using `pipx`, execute the command:
```shell
pipx install poetry
```

## Navigate to the project's main directory

If you're already in the main project folder, execute the command:
```shell
cd eyes
```

## Install project dependencies

Once in the project folder, use `poetry` to install all dependencies specified in the [`pyproject.toml`](/eyes/pyproject.toml) file:
```shell
poetry install
```
This command creates a virtual environment for the project (if one doesn't already exist) and installs all necessary dependencies.

## Activate the virtual environment

To activate the virtual environment managed by `poetry`, use the command:
```shell
poetry shell
```
This command launches a new shell where the virtual environment is activated, allowing you to execute commands and scripts in this environment's context.

## Adding dependencies to the project

You probably won't need to do this.
But if needed, where you would normally do:
```shell
pip install dependency_name
```
To add a dependency to this project, you should do:
```shell
poetry add dependency_name
```
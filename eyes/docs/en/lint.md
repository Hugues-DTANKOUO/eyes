# Using `mypy`, `black`, and `ruff` with poetry in the project

This file contains information about using mypy, black, and ruff with poetry in the project.

## mypy

[*`mypy`*](https://mypy.readthedocs.io/) is a static type checker for Python. It helps detect type errors before code execution.

## black

[*`black`*](https://black.readthedocs.io/) is a code formatter for Python. It applies consistent style rules to source code by automatically reformatting it.

## ruff

[*`ruff`*](https://github.com/jwkvam/ruff) is a linting tool for Python. It helps detect style errors, code quality issues, and coding convention violations.

## Static Code Analysis

To perform static analysis of your code with these three modules in this project, execute the following `poetry` command in the project's main directory:

```shell
poetry run lint
```
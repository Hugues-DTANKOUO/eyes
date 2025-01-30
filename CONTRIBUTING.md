# Contributing to `Eyes`

We're excited that you're interested in contributing to `Eyes`! All contributions are welcome: code improvements, bug fixes, documentation, suggestions, etc.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue using the provided bug report template. Make sure to include:

- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Screenshots if applicable

### Suggesting Improvements

For any improvement suggestions or feature requests, open an issue with a detailed description of the proposed enhancement. Explain why you think this improvement would be valuable and how it should work.

## Pull Requests

We warmly welcome pull requests. Here are the guidelines to follow when contributing:

#### 1. *Fork the repository* and follow the instructions to set up your workspace in [VS Code](/docs/utilisatation-vs-code.md)

#### 2. *Install dependencies* and ensure the project runs correctly on your system. [(poetry)](/eyes/docs/python-3-poetry.md)

#### 3. *Follow the project's code conventions*. For this Python project, we follow [PEP 8](https://peps.python.org/pep-0008/) ([Summary of PEP 8](/docs/PEP8-resume-fr.md)), so make sure you've read and apply it.

#### 4. *Write tests* for new features or bug fixes when possible.

#### 5. *Document your code*, especially new features. Make sure to add or update code comments and project documentation as needed.

#### 6. *Run existing tests* to ensure you haven't introduced any regressions.

In the [/eyes](/eyes/) directory, run:
```shell
poetry run check
```

#### 7. *Submit your pull request* with a detailed description of your changes. Include the context of what you've done and why.

### Pull Request Review Process

Each pull request will be reviewed by project maintainers. We may request changes or make suggestions before merging your contribution. We aim to respond to PRs within 2 days maximum, but this may vary depending on the volume of contributions.

## Code of Conduct

By contributing to this project, you agree to abide by its code of conduct. Any inappropriate behavior may result in your contribution being removed or being banned from participating.
You also agree to never claim partial or total ownership of this project. You have the right to be listed among the contributors and to use this project within the scope described by its license.
# EYES: Keep an eye on your business

All-in-one software for managing your company's lifecycle

![Eyes Logo](./assets/logo/eyes.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview

EYES is a comprehensive and modular business management solution designed to simplify and optimize operational processes. The project follows the principles of the [Agile Manifesto](docs/manifeste%20agile.md) to deliver a scalable solution that adapts to user needs.

### Project Goals

- Centralize business data management
- Provide an intuitive and high-performance interface
- Ensure data security and confidentiality
- Facilitate team collaboration
- Enable customization based on specific needs

## Features

### Data Management
- Flexible data modeling ([models](models/))
- Multiple database support (PostgreSQL, SQLite)
- Automated schema management

### Administration
- Secure administration interface
- User and role management
- Performance monitoring

### Collaboration
- Team data sharing
- Change history tracking
- Notification system

## Technologies Used

### Backend
- Python 3.11+
- SQLAlchemy ORM
- Poetry for dependency management
- Black, Ruff, and MyPy for code quality

### Database
- PostgreSQL support
- SQLite support
- Modular architecture for future extensions

### Development Tools
- Poetry for dependency management
- Unit testing with pytest
- Static code analysis with mypy and ruff
- Automatic formatting with black

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Hugues-DTANKOUO/Eyes.git
cd Eyes
```

2. [Install Poetry](eyes/docs/python-3-poetry.md) if not already installed.

3. Install dependencies:
```bash
cd eyes
poetry install
```

4. Verify installation:
```bash
poetry run check
```

For more details, check the [detailed installation guide](eyes/docs/python-3-poetry.md).

## Development

### Code Conventions
- [PEP 8 and naming conventions](docs/PEP8-resume-fr.md)
- [CapWords convention for classes](docs/CapWords-CamelCase.md)

### Testing and Validation
```bash
# Run tests
poetry run tests

# Static code analysis
poetry run lint

# Complete validation
poetry run check
```

## [Contributing](CONTRIBUTING.md)

We welcome contributions! See our [contribution guide](CONTRIBUTING.md) to get started.

### [VS Code Guide](docs/utilisatation-vs-code.md)
Detailed instructions for setting up and using VS Code for development.

## [License](LICENSE)

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

| Role | Full Name | Github | LinkedIn | Facebook |
|---------|---------------|--------|----------|----------|
| Project Lead | Hugues DTANKOUO | [@Hugues-DTANKOUO](https://github.com/Hugues-DTANKOUO) | [@dtankouo](https://linkedin.com/in/dtankouo) | [@ing.hugues.dtankouo](https://facebook.com/ing.hugues.dtankouo) |
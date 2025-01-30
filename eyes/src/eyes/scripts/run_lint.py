""" Script for running Ruff, Black and MyPy across all project modules. """

import subprocess

from eyes.application import (
    EYES,
    MODELS,
    Module,
)

MODULES: list[Module] = [EYES, MODELS]

LINTERS = ["black", "mypy"]


def run() -> None:
    """Execute Ruff, Black and Mypy across all project modules."""

    # Execute Ruff, Black and Mypy across all project modules
    print("Running Ruff, Black and Mypy across all project modules...")

    for module in MODULES:
        # Execute Ruff on the module
        print(f"Running Ruff on module {module.name}...")
        subprocess.run(["ruff", "check", module.path, "--fix"], check=True)

        for linter in LINTERS:
            print(f"Running {linter} on module {module.name}...")
            subprocess.run([linter, module.path], check=True)

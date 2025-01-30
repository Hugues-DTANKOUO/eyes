""" Scripts for running unit tests across all project modules. """

import subprocess

from eyes.application import (
    EYES,
    MODELS,
    Module,
)

MODULES: list[Module] = [EYES, MODELS]


def run() -> None:
    """Execute unit tests across all project modules."""

    print("Running unit tests across all project modules...")

    for module in MODULES:
        print(f"Running unit tests on module {module.name}...")
        subprocess.run(["pytest", module.path, "-v"])

""" Scripts d'exécution des tests unitaires sur l'ensemble des modules du projet. """

import subprocess

from eyes.application import (
    EYES,
    MODELS,
    Module,
)

MODULES: list[Module] = [EYES, MODELS]


def run() -> None:
    """Exécute les tests unitaires sur l'ensemble des modules du projet."""

    print("Exécution des tests unitaires sur l'ensemble des modules du projet...")

    for module in MODULES:
        print(f"Exécution des tests unitaires sur le module {module.name}...")
        subprocess.run(["pytest", module.path, "-v"])

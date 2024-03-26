""" Variables globales de l'application. """

from __future__ import annotations

import os


# Nom de l'application
APPLICATION_NAME: str = "Eyes"

# Chemin du répertoire courant
APPLICATION_DIR: str = os.path.dirname(os.path.realpath(__file__))

# Chemin du répertoire du projet
PROJECT_DIR: str = os.path.abspath(os.path.join(APPLICATION_DIR, *[os.pardir] * 3))

# Erreur d'appel invalide
INVALID_CALL_ERROR: str = "Cette méthode ne peut être appelée qu'une seule fois."


class ApplicationModuleError(Exception):
    """Erreur de module de l'application."""

    pass


class Module:
    """
    Représente un module de l'application.
    :param name: Nom du module.
    :param path: Chemin du module.
    """

    _name: str = ""
    _path: str = ""
    _eyes: Module | None = None
    _models: Module | None = None

    def __init__(self) -> None:
        """Constructeur du module."""
        pass

    def __str__(self) -> str:
        """Retourne une représentation du module."""

        return f"Module({self.name}, {self.path})"

    def __repr__(self) -> str:
        """Retourne une représentation du module."""

        return f"Module({self.name}, {self.path})"

    @property
    def name(self) -> str:
        """Retourne le nom du module."""

        return self._name

    @property
    def path(self) -> str:
        """Retourne le chemin du module."""

        return self._path

    def __create_module(self, name: str, directory_name: str) -> Module:
        """
        Crée un module.
        :param name: Nom du module.
        :param directory_name: Nom du répertoire du module.
        :return: Module créé.
        """

        if not self._name and not self._path:
            self._name = name
            self._path = os.path.join(PROJECT_DIR, directory_name)

            return self
        raise ApplicationModuleError(INVALID_CALL_ERROR)

    @property
    def eyes(self) -> Module:
        """Retourne le module de l'application."""

        if not self._eyes:
            self._eyes = self.__create_module(APPLICATION_NAME, "eyes")

        return self._eyes

    @property
    def models(self) -> Module:
        """Retourne le module de gestion des modèles."""

        if not self._models:
            self._models = self.__create_module("Models", "models")

        return self._models


# Liste des modules de l'application
EYES = Module().eyes
MODELS = Module().models

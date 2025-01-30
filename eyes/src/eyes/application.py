""" Global variables and core classes of the application. """

from __future__ import annotations

import os


# Application name
APPLICATION_NAME: str = "Eyes"

# Current directory path
APPLICATION_DIR: str = os.path.dirname(os.path.realpath(__file__))

# Project directory path
PROJECT_DIR: str = os.path.abspath(os.path.join(APPLICATION_DIR, *[os.pardir] * 3))

# Invalid call error message
INVALID_CALL_ERROR: str = "This method can only be called once."


class ApplicationModuleError(Exception):
    """Application module error."""

    pass


class Module:
    """
    Represents an application module.

    :param name: Module name.
    :param path: Module path.
    """

    _name: str = ""
    _path: str = ""
    _eyes: Module | None = None
    _models: Module | None = None

    def __init__(self) -> None:
        """Module constructor."""
        pass

    def __str__(self) -> str:
        """Returns a string representation of the module."""

        return f"Module({self.name}, {self.path})"

    def __repr__(self) -> str:
        """Returns a string representation of the module."""

        return f"Module({self.name}, {self.path})"

    @property
    def name(self) -> str:
        """Returns the module name."""

        return self._name

    @property
    def path(self) -> str:
        """Returns the module path."""

        return self._path

    def __create_module(self, name: str, directory_name: str) -> Module:
        """
        Creates a module.

        :param name: Module name.
        :param directory_name: Module directory name.
        :return: Created module.
        """

        if not self._name and not self._path:
            self._name = name
            self._path = os.path.join(PROJECT_DIR, directory_name)

            return self
        raise ApplicationModuleError(INVALID_CALL_ERROR)

    @property
    def eyes(self) -> Module:
        """Returns the application module."""

        if not self._eyes:
            self._eyes = self.__create_module(APPLICATION_NAME, "eyes")

        return self._eyes

    @property
    def models(self) -> Module:
        """Returns the models management module."""

        if not self._models:
            self._models = self.__create_module("Models", "models")

        return self._models


# List of application modules
EYES = Module().eyes
MODELS = Module().models

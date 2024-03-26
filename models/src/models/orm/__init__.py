from abc import ABC


class ORM(ABC):
    """
    Classe de base de gestion de la couche ORM.
    """

    class Table:
        """
        Classe de gestion des tables.
        """

        def __init__(self, name: str) -> None:
            """Constructeur de la table."""
            self._name = name

        @property
        def name(self) -> str:
            """Retourne le nom de la table."""
            return self._name

from abc import ABC, abstractmethod
from typing import Any


class ORM(ABC):
    """
    Classe de base de gestion de la couche ORM.
    """

    class Table(ABC):
        """
        Classe de gestion des tables.
        """

        name: str
        link_table: Any
        columns: list

    class Session(ABC):
        """
        Classe de gestion des sessions.
        """

        pass

    def __init__(self, *args, **kwargs) -> None:
        """Constructeur de la couche ORM."""
        pass

    @abstractmethod
    def get_session(self) -> Session:
        """
        Retourne une session.
        :return: Session.
        """

        pass

    @abstractmethod
    def close_session(self, *args, **kwargs) -> None:
        """
        Ferme une session.
        :param session: Session à fermer.
        """

        pass

    @abstractmethod
    def get_table(self, table_name: str) -> Table:
        """
        Retourne une table.
        :param table_name: Nom de la table.
        :return: Table.
        """

        pass

from abc import ABC, abstractmethod
from typing import Any, Type

from models.relational.metadata import ColumnType, ColumnMeta


class ORM(ABC):
    """
    Classe de base de gestion de la couche ORM.

    - Classes:
        - Table: Classe de gestion des tables.
        - Column: Classe de gestion des colonnes.
        - NoSuchTableError: Erreur de table inexistante.
    """

    class Table(ABC):
        """
        Classe de gestion des tables.

        - Attributs:
            - name: Nom de la table.
            - link_table: Table liée.
            - columns: Colonnes.
        """

        name: str
        link_table: Any
        columns: list[ColumnMeta]

    class Column(ABC):
        """
        Classe de gestion des colonnes.

        - Attributs:
            - name: Nom de la colonne.
            - type: Type de la colonne.
            - length: Longueur de la colonne.
            - nullable: Colonne nullable.
            - primary_key: Colonne clé primaire.
            - unique: Colonne unique.
        """

        name: str
        type: ColumnType
        length: int
        nullable: bool
        primary_key: bool
        unique: bool

    class NoSuchTableError(Exception):
        """
        Erreur de table inexistante.
        """

        pass

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Constructeur de la couche ORM pour SQLAlchemy.
        :param engine_url: URL de connexion à la base de données.
        """

        pass

    @staticmethod
    def get_no_such_table_error() -> Type[Exception]:
        """
        Retourne l'erreur de table inexistante.
        :return: Erreur de table inexistante.
        """

        return Exception

    @abstractmethod
    def close_session(self, *args: Any, **kwargs: Any) -> None:
        """
        Ferme une session.
        :param *args: Arguments.
        :param **kwargs: Arguments nommés.
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

    @abstractmethod
    def create_table(self, *args: Any, **kwargs: Any) -> Table:
        """
        Crée une table.
        :param *args: Arguments.
        :param **kwargs: Arguments nommés.
        :return: Table.
        """

        pass

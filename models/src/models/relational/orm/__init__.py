from abc import ABC, abstractmethod
from typing import Any, Type

from models.relational.metadata import (
    ColumnType,
    ColumnMeta,
    ForeignKeyColumnMeta,
    ForeignKeyAction,
    UniqueColumnsMeta,
)


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
            - link_table: Table de l'ORM.
            - columns_meta: Métadonnées des colonnes.
        """

        name: str
        link_table: Any
        columns_meta: list[ColumnMeta | ForeignKeyColumnMeta]
        unique_constraints: list[UniqueColumnsMeta]

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
            - default: Valeur par défaut de la colonne.
            - link_column: Colonne de l'ORM.
        """

        name: str
        type: ColumnType
        length: int | None
        nullable: bool
        primary_key: bool
        unique: bool
        default: Any
        link_column: Any

    class ForeignKeyColumn(Column):
        """
        Classe de gestion des colonnes de clé étrangère.

        - Attributs:
            - name: Nom de la colonne.
            - type: Type de la colonne.
            - length: Longueur de la colonne.
            - nullable: Colonne nullable.
            - primary_key: Colonne clé primaire.
            - unique: Colonne unique.
            - default: Valeur par défaut de la colonne.
            - foreign_table_name: Nom de la table étrangère.
            - foreign_column_name: Nom de la colonne étrangère.
            - on_delete: Action de suppression.
            - on_update: Action de mise à jour.
        """

        foreign_table_name: str
        foreign_column_name: str
        on_delete: ForeignKeyAction = ForeignKeyAction.NO_ACTION
        on_update: ForeignKeyAction = ForeignKeyAction.NO_ACTION

    class UniqueConstraint(ABC):
        """
        Classe de gestion des contraintes d'unicité.

        - Attributs:
            - name: Nom de la contrainte.
            - columns: Colonnes.
            - link_constraint: Contrainte de l'ORM.
        """

        name: str
        columns: set[str]
        link_constraint: Any

    class NoSuchTableError(Exception):
        """
        Erreur de table inexistante.
        """

        pass

    class CreateTableError(Exception):
        """
        Erreur de création de table.
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
    def create_table(
        self,
        table_name: str,
        columns: list[ColumnMeta | ForeignKeyColumnMeta],
        unique_constraints_columns: list[UniqueColumnsMeta] | None = None,
    ) -> Table:
        """
        Récupère ou crée une table.
        :param table_name: Nom de la table.
        :param columns: Colonnes de la table.
        :param unique_constraints_columns: Contraintes d'unicité.
        :return: Table.
        """

        pass

    @abstractmethod
    def get_tables(self) -> dict[str, Table]:
        """
        Récupère les tables de la base de données.
        :return: Tables.
        """

        pass

    @abstractmethod
    def get_table(self, table_name: str) -> Table:
        """
        Récupère une table de la base de données.
        :param table_name: Nom de la table.
        :return: Table.
        """

        pass

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Type

from models.relational.metadata import (
    ColumnMeta,
    ForeignKeyColumnMeta,
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
            - unique_constraints: Contraintes d'unicité.
            - orm: ORM.
        """

        name: str
        link_table: Any
        columns_meta: list[ColumnMeta | ForeignKeyColumnMeta]
        unique_constraints: list[UniqueColumnsMeta]
        orm: ORM

        class AddColumnError(Exception):
            """
            Erreur d'ajout de colonne.
            """

            pass

        @abstractmethod
        def add_column(
            self,
            column: ColumnMeta | ForeignKeyColumnMeta,
        ) -> ORM.Column:
            """
            Ajoute une colonne à la table.
            :param column: Colonne à créer.
            :return: Colonne.
            """

            pass

    class Column(ABC):
        """
        Classe de gestion des colonnes.

        - Attributs:
            - meta: Métadonnées de la colonne.
            - link_column: Colonne de l'ORM.
            - orm: ORM.
        """

        meta: ColumnMeta
        link_column: Any
        orm: ORM

    class ForeignKeyColumn(Column):
        """
        Classe de gestion des colonnes de clé étrangère.

        - Attributs:
            - meta: Métadonnées de la colonne.
            - link_column: Colonne de l'ORM.
            - orm: ORM.
        """

        meta: ForeignKeyColumnMeta

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

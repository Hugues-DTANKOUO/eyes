from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Type
from enum import Enum

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

    schema: str | None

    class SQL_Verbs(str, Enum):
        """
        Verbes SQL.
        """

        SELECT = "SELECT"
        INSERT = "INSERT"
        UPDATE = "UPDATE"
        DELETE = "DELETE"
        CREATE = "CREATE"
        DROP = "DROP"
        ALTER = "ALTER"
        ADD = "ADD"
        TO = "TO"
        FOREIGNKEY = "FOREIGN KEY"
        REFERENCES = "REFERENCES"
        PRIMARYKEY = "PRIMARY KEY"
        UNIQUE = "UNIQUE"
        CONSTRAINT = "CONSTRAINT"
        NOT_NULL = "NOT NULL"
        DEFAULT = "DEFAULT"
        FROM = "FROM"
        WHERE = "WHERE"
        ALTER_TABLE = "ALTER TABLE"
        TABLE = "TABLE"
        ALTER_COLUMN = "ALTER COLUMN"
        ADD_COLUMN = "ADD COLUMN"
        DROP_COLUMN = "DROP COLUMN"
        RENAME_COLUMN = "RENAME COLUMN"
        ON_DELETE = "ON DELETE"
        CASCADE = "CASCADE"
        ON_UPDATE = "ON UPDATE"
        RENAME_TO = "RENAME TO"

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

        _name: str
        _link_table: Any
        columns: list[ORM.Column | ORM.ForeignKeyColumn]
        unique_constraints: list[UniqueColumnsMeta]
        orm: ORM

        class AddColumnError(Exception):
            """
            Erreur d'ajout de colonne.
            """

            pass

        @abstractmethod
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """
            Constructeur de la classe Table.
            :param *args: Arguments.
            :param **kwargs: Arguments nommés.
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

        @abstractmethod
        def get_column(self, name: str) -> ORM.Column | ORM.ForeignKeyColumn:
            """
            Récupère une colonne de la table.
            :param name: Nom de la colonne.
            :return: Colonne.
            """

            pass

        @property
        @abstractmethod
        def name(self) -> str:
            """
            Retourne le nom de la table.
            :return: Nom de la table.
            """

            pass

        @name.setter
        @abstractmethod
        def name(self, name: str) -> None:
            """
            Modifie le nom de la table.
            :param name: Nom de la table.
            """

            pass

        def _table_name_for_request(self, name: str | None = None) -> str:
            """
            Retourne le nom de la table pour une requête SQL.
            :param name: Nom de la table.
            :return: Nom de la table pour une requête SQL.
            """
            name = name or self.name
            return f'{self.orm.schema}."{name}"' if self.orm.schema else name

    class Column(ABC):
        """
        Classe de gestion des colonnes.

        - Attributs:
            - meta: Métadonnées de la colonne.
            - link_column: Colonne de l'ORM.
            - orm: ORM.
        """

        meta: ColumnMeta
        _link_column: Any
        orm: ORM

        @abstractmethod
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """
            Constructeur de la classe Column.
            :param *args: Arguments.
            :param **kwargs: Arguments nommés.
            """

            pass

        @abstractmethod
        def set_name(self, name: str) -> ORM.Column | ORM.ForeignKeyColumn:
            """
            Modifie le nom de la colonne.
            :param name: Nom de la colonne.
            :return: Colonne.
            """

            pass

        @staticmethod
        def _name_for_request(name: str) -> str:
            """
            Retourne le nom de la colonne pour une requête SQL.
            :param name: Nom de la colonne.
            :return: Nom de la colonne pour une requête SQL.
            """
            return f'"{name}"'

        @staticmethod
        def _nullable_for_request(nullable: bool) -> str:
            """
            Retourne la contrainte de nullabilité pour une requête SQL.
            :param nullable: Nullabilité de la colonne.
            :return: Contrainte de nullabilité pour une requête SQL.
            """
            return ORM.SQL_Verbs.NOT_NULL.value if not nullable else ""

        @staticmethod
        def _default_for_request(default: Any) -> str:
            """
            Retourne la valeur par défaut pour une requête SQL.
            :return: Valeur par défaut pour une requête SQL.
            """
            default_rq = ""
            if default is not None:
                default_rq = f"{ORM.SQL_Verbs.DEFAULT.value} "
                if isinstance(default, str):
                    default_rq += f"'{default}'"
                else:
                    default_rq += default
            return default_rq

        @staticmethod
        def _primary_key_for_request(primary_key: bool) -> str:
            """
            Retourne la contrainte de clé primaire pour une requête SQL.
            :param primary_key: Clé primaire de la colonne.
            :return: Contrainte de clé primaire pour une requête SQL.
            """
            return ORM.SQL_Verbs.PRIMARYKEY.value if primary_key else ""

        @staticmethod
        def _unique_for_request(unique: bool) -> str:
            """
            Retourne la contrainte d'unicité pour une requête SQL.
            :param unique: Unicité de la colonne.
            :return: Contrainte d'unicité pour une requête SQL.
            """
            return ORM.SQL_Verbs.UNIQUE.value if unique else ""

        @staticmethod
        def _foreign_key_for_request(
            column: ColumnMeta | ForeignKeyColumnMeta, foreign_table_name: str
        ) -> str:
            """
            Retourne la contrainte de clé étrangère pour une requête SQL.
            :param column: Colonne.
            :return: Contrainte de clé étrangère pour une requête SQL.
            """
            foreign_key = ""
            if isinstance(column, ForeignKeyColumnMeta):
                foreign_key = (
                    f'FOREIGN KEY ("{column.name}") REFERENCES '
                    f"{foreign_table_name}"
                    f' ("{column.foreign_column_name}")'
                    f" ON DELETE {column.on_delete.value}"
                    f" ON UPDATE {column.on_update.value}"
                )
            return foreign_key

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
        _link_constraint: Any

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

    class SQLExecutionError(Exception):
        """
        Erreur d'exécution de requête SQL.
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

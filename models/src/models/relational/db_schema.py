"""
Structure de base d'un modèle relationnel de données.

- Classes:
    - Database: Base de données.
    - SQLite: Base de données SQLite.
    - PostgreSQL: Base de données PostgreSQL.
    - MySQL: Base de données MySQL.
    - OracleDB: Base de données Oracle.
    - SQLServer: Base de données SQL Server.
    - Table: Table de la base de données.
    - Column: Colonne d'une table.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Generic, TypeVar, Type, cast
from abc import ABC, abstractmethod

from models.relational.orm import ORM
from models.relational.config import DbConfig, DataBaseType
from models.relational.metadata import ColumnMeta, ColumnType


ORM_TYPE = TypeVar("ORM_TYPE", bound=ORM)
TABLE_ORM_TYPE = TypeVar("TABLE_ORM_TYPE", bound=ORM.Table)


class Database(Generic[ORM_TYPE, TABLE_ORM_TYPE], ABC):
    """
    Classe abstraite représentant une base de données.

    :param _engine_url: URL de connexion à la base de données.
    :param _name: Nom de la base de données.
    :param _type: Type de la base de données.
    :param _orm: Couche ORM de la base de données.
    """

    _engine_url: str
    _name: str
    _type: DataBaseType
    _orm: ORM_TYPE

    def __init__(self, db_config: DbConfig | Path, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Constructeur de la base de données.

        :param db_config: Configuration de la base de données.
        :param orm_class_: Classe de la couche ORM.
        """

        if isinstance(db_config, DbConfig):
            self._engine_url = db_config.get_engine_url()
            self._type = db_config.type
            self._name = db_config.database
        elif isinstance(db_config, Path):
            if db_config.suffix == ".db":
                self._engine_url = "sqlite:///" + str(db_config)
                self._type = DataBaseType.SQLITE
                self._name = db_config.stem
            else:
                raise ValueError("Le type de base de données n'est pas supporté.")
        else:
            raise ValueError("La configuration de la base de données est invalide.")
        self._orm = orm_class_(self._engine_url)

    @property
    def name(self) -> str:
        """Retourne le nom de la base de données."""
        return self._name

    def disconnection(self) -> None:
        """Déconnecte de la base de données."""
        self._orm.close_session()

    def get_or_create_orm_table(
        self,
        table_name: str,
        columns: list[ColumnMeta] | None = None,
        ensure_exists: bool = False,
    ) -> Type[TABLE_ORM_TYPE]:
        """
        Récupère ou crée une table du type de la couche ORM.
        :param table_name: Nom de la table.
        :param columns: Colonnes de la table.
        :param ensure_exists: Assure l'existence de la table.
        :return: Table.
        """

        try:
            return cast(
                Type[TABLE_ORM_TYPE],
                self._orm.get_or_create_table(table_name, columns, ensure_exists),
            )
        except self._orm.NoSuchTableError as e:
            raise self._orm.NoSuchTableError(e) from e
        except self._orm.CreateTableError as e:
            raise self._orm.CreateTableError(e) from e
        except Exception as e:
            raise Exception(
                f"Impossible de récupérer ou créer la table {table_name}."
            ) from e

    @abstractmethod
    def execute(self, query: str) -> Any:
        """
        Exécute une requête sur la base de données.

        :param query: Requête à exécuter.
        :return: Résultat de la requête.
        """
        pass


class SQLite(Database[ORM_TYPE, TABLE_ORM_TYPE]):
    """
    Représente une base de données SQLite.
    """

    def __init__(self, db_config: Path, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Constructeur de la base de données SQLite.

        :param db_config: Configuration de la base de données.
        :param orm_class_: Classe de la couche ORM.
        """
        super().__init__(db_config, orm_class_)

    def execute(self, query: str) -> Any:
        """
        Exécute une requête sur la base de données SQLite.

        :param query: Requête à exécuter.
        :return: Résultat de la requête.
        """
        pass


class PostgreSQL(Database[ORM_TYPE, TABLE_ORM_TYPE]):
    """
    Représente une base de données PostgreSQL.
    """

    def __init__(self, db_config: DbConfig, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Constructeur de la base de données PostgreSQL.

        :param db_config: Configuration de la base de données.
        :param orm_class_: Classe de la couche ORM.
        """
        super().__init__(db_config, orm_class_)

    def execute(self, query: str) -> Any:
        """
        Exécute une requête sur la base de données PostgreSQL.

        :param query: Requête à exécuter.
        :return: Résultat de la requête.
        """
        pass


class MySQL(Database[ORM_TYPE, TABLE_ORM_TYPE]):
    """
    Représente une base de données MySQL.
    """

    def __init__(self, db_config: DbConfig, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Constructeur de la base de données MySQL.

        :param db_config: Configuration de la base de données.
        :param orm_class_: Classe de la couche ORM.
        """
        super().__init__(db_config, orm_class_)

    def execute(self, query: str) -> Any:
        """
        Exécute une requête sur la base de données MySQL.

        :param query: Requête à exécuter.
        :return: Résultat de la requête.
        """
        pass


class OracleDB(Database[ORM_TYPE, TABLE_ORM_TYPE]):
    """
    Représente une base de données Oracle.
    """

    def __init__(self, db_config: DbConfig, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Constructeur de la base de données Oracle.

        :param db_config: Configuration de la base de données.
        :param orm_class_: Classe de la couche ORM.
        """
        super().__init__(db_config, orm_class_)

    def execute(self, query: str) -> Any:
        """
        Exécute une requête sur la base de données Oracle.

        :param query: Requête à exécuter.
        :return: Résultat de la requête.
        """
        pass


class SQLServer(Database[ORM_TYPE, TABLE_ORM_TYPE]):
    """
    Représente une base de données SQL Server.
    """

    def __init__(self, db_config: DbConfig, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Constructeur de la base de données SQL Server.

        :param db_config: Configuration de la base de données.
        """
        super().__init__(db_config, orm_class_)

    def execute(self, query: str) -> Any:
        """
        Exécute une requête sur la base de données SQL Server.

        :param query: Requête à exécuter.
        :return: Résultat de la requête.
        """
        pass


class Table(Generic[ORM_TYPE, TABLE_ORM_TYPE]):
    """
    Représente une table de la base de données.

    :param name: Nom de la table.
    :param database: Base de données à laquelle appartient la table.
    :param columns: Colonnes de la table.
    """

    db_name: str
    vb_name: str
    database: Database[ORM_TYPE, TABLE_ORM_TYPE]
    _columns: list[Column]
    link_table: Type[TABLE_ORM_TYPE]

    def __init__(
        self,
        name: str,
        database: Database[ORM_TYPE, TABLE_ORM_TYPE],
        columns: list[ColumnMeta] | None = None,
        ensure_exists: bool = True,
    ) -> None:
        """
        Constructeur de la table.

        :param name: Nom de la table.
        :param database: Base de données à laquelle appartient la table.
        :param columns: Colonnes de la table.
        :param ensure_exists: Indique si la table doit exister.
        """

        try:
            table = database.get_or_create_orm_table(name, columns, ensure_exists)
            self.db_name = table.name
            self.vb_name = name
            self.database = database
            self._columns = [Column(column, self) for column in table.columns]
            self.link_table = cast(Type[TABLE_ORM_TYPE], table.link_table)
        except database._orm.NoSuchTableError as e:
            raise database._orm.NoSuchTableError(e) from e
        except database._orm.CreateTableError as e:
            raise database._orm.CreateTableError(e) from e
        except Exception as e:
            raise Exception(f"Erreur lors de la création de la table {name}.") from e

    def __str__(self) -> str:
        """Retourne une représentation de la table."""
        return f"Table {self.vb_name} de la base de données {self.database.name}"

    @property
    def name(self) -> str:
        """Retourne le nom de la table."""
        return self.vb_name

    @property
    def primary_key(self) -> Column:
        """
        Retourne la colonne clé primaire de la table.

        :return: Colonne clé primaire.
        """
        for column in self._columns:
            if column.primary_key:
                return column
        raise ValueError(
            f"Aucune colonne clé primaire n'existe dans la table {self.vb_name}."
        )

    @property
    def columns(self) -> list[Column]:
        """Retourne les colonnes de la table."""
        return self._columns

    def get_column(self, column_name: str) -> Column:
        """
        Retourne une colonne de la table.

        :param column_name: Nom de la colonne.
        :return: Colonne.
        """
        for column in self._columns:
            if column.name == column_name:
                return column
        raise ValueError(
            f"La colonne {column_name} n'existe pas dans la table {self.vb_name}."
        )


class Column:
    """
    Représente une colonne d'une table.

    :param name: Nom de la colonne.
    :param type: Type de la colonne.
    :param length: Longueur de la colonne.
    :param nullable: Indique si la colonne peut être nulle.
    :param primary_key: Indique si la colonne est une clé primaire.
    :param table: Table à laquelle appartient la colonne.
    """

    name: str
    type: ColumnType
    length: int | None
    nullable: bool
    primary_key: bool
    table: Table

    def __init__(self, meta_data: ColumnMeta, table: Table) -> None:
        """
        Constructeur de la colonne.

        :param meta_data: Métadonnées de la colonne.
        :param table: Table à laquelle appartient la colonne.
        """
        self.name = meta_data["name"]
        self.type = meta_data["type"]
        self.length = meta_data["length"]
        self.nullable = meta_data["nullable"]
        self.primary_key = meta_data["primary_key"]
        self.table = table

    def __str__(self) -> str:
        """Retourne une représentation de la colonne."""
        return f"Colonne {self.name} de type {self.type.value} de la table {self.table.vb_name}"


class ForeignKeyColumn(Column):
    """
    Représente une colonne de clé étrangère.

    :param name: Nom de la colonne.
    :param type: Type de la colonne.
    :param length: Longueur de la colonne.
    :param nullable: Indique si la colonne peut être nulle.
    :param primary_key: Indique si la colonne est une clé primaire.
    :param table: Table à laquelle appartient la colonne.
    :param foreign_table: Table étrangère.
    :param foreign_column: Colonne étrangère.
    """

    foreign_table: Table
    foreign_column: Column

    def __init__(
        self,
        meta_data: ColumnMeta,
        table: Table,
        foreign_table_name: str,
        foreign_column_name: str,
    ) -> None:
        """
        Constructeur de la colonne de clé étrangère.

        :param meta_data: Métadonnées de la colonne.
        :param table: Table à laquelle appartient la colonne.
        :param foreign_table_name: Nom de la table étrangère.
        :param foreign_column_name: Nom de la colonne étrangère.
        """
        super().__init__(meta_data, table)
        self.foreign_table = Table(foreign_table_name, table.database)
        self.foreign_column = self.foreign_table.get_column(foreign_column_name)

    def __str__(self) -> str:
        """Retourne une représentation de la colonne de clé étrangère."""
        return (
            f"Colonne {self.name} de type {self.type.value} de la table"
            f" {self.table.vb_name} avec clé étrangère vers la table {self.foreign_table.vb_name}"
        )

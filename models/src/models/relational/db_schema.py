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

    def get_table(self, table_name: str) -> Type[TABLE_ORM_TYPE]:
        """
        Retourne les métadonnées d'une table.

        :param table_name: Nom de la table.
        :return: Métadonnées de la table.
        """
        try:
            return cast(Type[TABLE_ORM_TYPE], self._orm.get_table(table_name))
        except ValueError as e:
            raise ValueError(e) from e

    def create_table(
        self, table_name: str, columns: list[ColumnMeta]
    ) -> Type[TABLE_ORM_TYPE]:
        """
        Crée une table.

        :param table_name: Nom de la table.
        :param columns: Colonnes de la table.
        :return: Table créée.
        """
        try:
            return cast(
                Type[TABLE_ORM_TYPE], self._orm.create_table(table_name, columns)
            )
        except Exception as e:
            raise Exception(f"Impossible de créer la table : {e}.") from e

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
    columns: list[Column]
    link_table: Type[TABLE_ORM_TYPE]

    def __init__(
        self,
        name: str,
        database: Database[ORM_TYPE, TABLE_ORM_TYPE],
        columns: list[ColumnMeta] | None = None,
        ensure_exists: bool = True,
        orm_class: Type[ORM_TYPE] = cast(Type[ORM_TYPE], ORM),
    ) -> None:
        """
        Constructeur de la table.

        :param name: Nom de la table.
        :param database: Base de données à laquelle appartient la table.
        :param columns: Colonnes de la table.
        :param ensure_exists: Indique si la table doit exister.
        """

        try:
            table = database.get_table(name)
            self.db_name = table.name
            self.vb_name = name
            self.database = database
            self.columns = [Column(column, self) for column in table.columns]
            self.link_table = cast(Type[TABLE_ORM_TYPE], table.link_table)
        except orm_class.get_no_such_table_error() as e:
            if ensure_exists:
                raise orm_class.NoSuchTableError(e) from e
            if columns is None:
                raise ValueError("Les colonnes de la table sont obligatoires.")
            table = database.create_table(name, columns)
            self.db_name = table.name
            self.vb_name = name
            self.database = database
            self.columns = [Column(column, self) for column in columns]
            self.link_table = cast(Type[TABLE_ORM_TYPE], table.link_table)

    def __str__(self) -> str:
        """Retourne une représentation de la table."""
        return f"Table {self.vb_name} de la base de données {self.database.name}"

    @property
    def name(self) -> str:
        """Retourne le nom de la table."""
        return self.vb_name


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

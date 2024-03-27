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


ORM_TYPE = TypeVar("ORM_TYPE", bound=ORM)
TABLE_ORM_TYPE = TypeVar("TABLE_ORM_TYPE", bound=ORM.Table)
SESSION_ORM_TYPE = TypeVar("SESSION_ORM_TYPE", bound=ORM.Session)
T = TypeVar("T", bound=ORM.Table)


class Database(Generic[ORM_TYPE, TABLE_ORM_TYPE, SESSION_ORM_TYPE], ABC):
    """
    Classe abstraite représentant une base de données.
    """

    _engine_url: str
    _name: str
    _type: DataBaseType
    _orm: ORM_TYPE

    def __init__(self, db_config: DbConfig | Path, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Constructeur de la base de données.

        :param db_config: Configuration de la base de données.
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

    def connect(self) -> SESSION_ORM_TYPE:
        """Connecte à la base de données."""
        return cast(SESSION_ORM_TYPE, self._orm.get_session())

    def disconnect(self) -> None:
        """Déconnecte de la base de données."""
        self._orm.close_session()

    @abstractmethod
    def get_table(self, table_name: str) -> TABLE_ORM_TYPE:
        """
        Retourne les métadonnées d'une table.

        :param table_name: Nom de la table.
        :return: Métadonnées de la table.
        """
        pass

    @abstractmethod
    def execute(self, query: str) -> Any:
        """
        Exécute une requête sur la base de données.

        :param query: Requête à exécuter.
        :return: Résultat de la requête.
        """
        pass


class SQLite(Database[ORM_TYPE, TABLE_ORM_TYPE, SESSION_ORM_TYPE]):
    """
    Représente une base de données SQLite.
    """

    def __init__(self, db_config: Path, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Constructeur de la base de données SQLite.

        :param db_config: Configuration de la base de données.
        """
        super().__init__(db_config, orm_class_)

    def get_table(self, table_name: str) -> TABLE_ORM_TYPE:
        """
        Retourne les métadonnées d'une table.

        :param table_name: Nom de la table.
        :return: Métadonnées de la table.
        """
        raise NotImplementedError

    def execute(self, query: str) -> Any:
        """
        Exécute une requête sur la base de données SQLite.

        :param query: Requête à exécuter.
        :return: Résultat de la requête.
        """
        pass


class PostgreSQL(Database[ORM_TYPE, TABLE_ORM_TYPE, SESSION_ORM_TYPE]):
    """
    Représente une base de données PostgreSQL.
    """

    def __init__(self, db_config: DbConfig, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Constructeur de la base de données PostgreSQL.

        :param db_config: Configuration de la base de données.
        """
        super().__init__(db_config, orm_class_)

    def get_table(self, table_name: str) -> TABLE_ORM_TYPE:
        """
        Retourne les métadonnées d'une table.

        :param table_name: Nom de la table.
        :return: Métadonnées de la table.
        """
        raise NotImplementedError

    def execute(self, query: str) -> Any:
        """
        Exécute une requête sur la base de données PostgreSQL.

        :param query: Requête à exécuter.
        :return: Résultat de la requête.
        """
        pass


class MySQL(Database[ORM_TYPE, TABLE_ORM_TYPE, SESSION_ORM_TYPE]):
    """
    Représente une base de données MySQL.
    """

    def __init__(self, db_config: DbConfig, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Constructeur de la base de données MySQL.

        :param db_config: Configuration de la base de données.
        """
        super().__init__(db_config, orm_class_)

    def get_table(self, table_name: str) -> TABLE_ORM_TYPE:
        """
        Retourne les métadonnées d'une table.

        :param table_name: Nom de la table.
        :return: Métadonnées de la table.
        """
        raise NotImplementedError

    def execute(self, query: str) -> Any:
        """
        Exécute une requête sur la base de données MySQL.

        :param query: Requête à exécuter.
        :return: Résultat de la requête.
        """
        pass


class OracleDB(Database[ORM_TYPE, TABLE_ORM_TYPE, SESSION_ORM_TYPE]):
    """
    Représente une base de données Oracle.
    """

    def __init__(self, db_config: DbConfig, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Constructeur de la base de données Oracle.

        :param db_config: Configuration de la base de données.
        """
        super().__init__(db_config, orm_class_)

    def get_table(self, table_name: str) -> TABLE_ORM_TYPE:
        """
        Retourne les métadonnées d'une table.

        :param table_name: Nom de la table.
        :return: Métadonnées de la table.
        """
        raise NotImplementedError

    def execute(self, query: str) -> Any:
        """
        Exécute une requête sur la base de données Oracle.

        :param query: Requête à exécuter.
        :return: Résultat de la requête.
        """
        pass


class SQLServer(Database[ORM_TYPE, TABLE_ORM_TYPE, SESSION_ORM_TYPE]):
    """
    Représente une base de données SQL Server.
    """

    def __init__(self, db_config: DbConfig, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Constructeur de la base de données SQL Server.

        :param db_config: Configuration de la base de données.
        """
        super().__init__(db_config, orm_class_)

    def get_table(self, table_name: str) -> TABLE_ORM_TYPE:
        """
        Retourne les métadonnées d'une table.

        :param table_name: Nom de la table.
        :return: Métadonnées de la table.
        """
        raise NotImplementedError

    def execute(self, query: str) -> Any:
        """
        Exécute une requête sur la base de données SQL Server.

        :param query: Requête à exécuter.
        :return: Résultat de la requête.
        """
        pass


class Table(Generic[ORM_TYPE, TABLE_ORM_TYPE, SESSION_ORM_TYPE]):
    """
    Représente une table de la base de données.

    :param name: Nom de la table.
    :param database: Base de données à laquelle appartient la table.
    :param columns: Colonnes de la table.
    """

    db_name: str
    vb_name: str
    database: Database[ORM_TYPE, TABLE_ORM_TYPE, SESSION_ORM_TYPE]
    columns: list[Column]
    link_table: TABLE_ORM_TYPE

    def __init__(
        self, name: str, database: Database[ORM_TYPE, TABLE_ORM_TYPE, SESSION_ORM_TYPE]
    ) -> None:
        """
        Constructeur de la table.

        :param name: Nom de la table.
        :param database: Base de données à laquelle appartient la table.
        """

        meta_data = database.get_table(name)
        self.db_name = meta_data.name
        self.vb_name = name
        self.database = database
        self.columns = meta_data.columns
        self.link_table = meta_data.link_table

    def __str__(self) -> str:
        """Retourne une représentation de la table."""
        return f"Table {self.vb_name} de la base de données {self.database.name}"


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
    type: str
    length: int | None
    nullable: bool
    primary_key: bool
    table: Table

    def __init__(
        self,
        name: str,
        type: str,
        length: int,
        nullable: bool,
        primary_key: bool,
        table: Table,
    ) -> None:
        """
        Constructeur de la colonne.

        :param name: Nom de la colonne.
        :param type: Type de la colonne.
        :param length: Longueur de la colonne.
        :param nullable: Indique si la colonne peut être nulle.
        :param primary_key: Indique si la colonne est une clé primaire.
        :param table: Table à laquelle appartient la colonne.
        """
        self.name = name
        self.type = type
        self.length = length
        self.nullable = nullable
        self.primary_key = primary_key
        self.table = table

    def __str__(self) -> str:
        """Retourne une représentation de la colonne."""
        return f"Colonne {self.name} de type {self.type}"

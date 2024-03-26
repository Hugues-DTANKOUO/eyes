"""
Structure de base d'un modèle relationnel de données.

- Classes:
    - DbConfig: Configuration d'une base de données.
    - DataBaseType: Types de base de données.
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
from enum import Enum
from typing import Any, Generic, TypeVar, Type
from pydantic import BaseModel, Field, validator
from abc import ABC, abstractmethod

from models.orm import ORM


TABLE_ORM_TYPE = TypeVar("TABLE_ORM_TYPE", bound=ORM.Table)


class DbConfig(BaseModel):
    """
    Eléments de configuration d'une base de données.

    :param host: Adresse du serveur de base de données.
    :param port: Port du serveur de base de données.
    :param type: Type de base de données.
    :param user: Nom d'utilisateur de la base de données.
    :param password: Mot de passe de la base de données.
    :param database: Nom de la base de données.
    """

    host: str = Field("localhost", title="Adresse du serveur de base de données")
    port: int = Field(..., title="Port du serveur de base de données")
    type: DataBaseType = Field(..., title="Type de base de données")
    user: str = Field("root", title="Nom d'utilisateur de la base de données")
    password: str = Field(..., title="Mot de passe de la base de données")
    database: str = Field("test", title="Nom de la base de données")

    def __init__(
        self,
        host: str,
        user: str,
        type: DataBaseType,
        password: str,
        database: str,
        port: int | None = None,
    ) -> None:
        """
        Constructeur de la configuration de la base de données.

        :param host: Adresse du serveur de base de données.
        :param user: Nom d'utilisateur de la base de données.
        :param type: Type de base de données.
        :param password: Mot de passe de la base de données.
        :param database: Nom de la base de données.
        :param port: Port du serveur de base de données.
        """

        if port is None:
            port = type.default_port()

        super().__init__(
            host=host,
            port=port,
            type=type,
            user=user,
            password=password,
            database=database,
        )

    def __str__(self) -> str:
        """Retourne une représentation de la configuration de la base de données."""
        return f"DbConfig({self.host}, {self.port}, {self.user}, {self.database})"

    def __repr__(self) -> str:
        """Retourne une représentation de la configuration de la base de données."""
        return f"DbConfig({self.host}, {self.port}, {self.user}, {self.database})"

    # Validateur pour le port
    @validator("port")
    def port_must_be_valid(cls, value: int) -> int:
        """
        Vérifie que le port est un entier positif.

        :param value: Port du serveur de base de données.
        :return: Port du serveur de base de données.
        """
        if not (isinstance(value, int) or 1 <= abs(value) <= 65535):
            raise ValueError(
                "Le port doit être un entier positif compris entre 1 et 65535."
            )
        return abs(value)


class DataBaseType(Enum):
    """Types de base de données."""

    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    ORACLE = "oracle"
    SQLSERVER = "sqlserver"

    def __str__(self) -> str:
        """Retourne une représentation du type de base de données."""
        return self.value

    def default_port(self) -> int:
        """Retourne le port par défaut du type de base de données."""

        return {
            DataBaseType.MYSQL: 3306,
            DataBaseType.POSTGRESQL: 5432,
            DataBaseType.SQLITE: 0,
            DataBaseType.ORACLE: 1521,
            DataBaseType.SQLSERVER: 1433,
        }[self]


class Database(Generic[TABLE_ORM_TYPE], ABC):
    """
    Classe abstraite représentant une base de données.
    """

    _db_config: DbConfig | str
    _name: str
    _type: DataBaseType

    class TableMetaData(BaseModel):
        """
        Métadonnées d'une table.

        :param name: Nom de la table.
        :param columns: Colonnes de la table.
        :param link_table: ORM de la table.
        """

        name: str = Field(..., title="Nom de la table")
        columns: list[Column] = Field([], title="Colonnes de la table")
        link_table: Type[ORM.Table] = Field(..., title="ORM de la table")

    def __init__(self, db_config: DbConfig | Path) -> None:
        """
        Constructeur de la base de données.

        :param db_config: Configuration de la base de données.
        """

        if isinstance(db_config, DbConfig):
            self._db_config = db_config
            self._type = db_config.type
            self._name = db_config.database
        elif isinstance(db_config, Path):
            if db_config.suffix == ".db":
                self._db_config = "sqlite:///" + str(db_config)
                self._type = DataBaseType.SQLITE
                self._name = db_config.stem
            else:
                raise ValueError("Le type de base de données n'est pas supporté.")
        else:
            raise ValueError("La configuration de la base de données est invalide.")

    @property
    def name(self) -> str:
        """Retourne le nom de la base de données."""
        return self._name

    @abstractmethod
    def connect(self) -> Any:
        """Connecte à la base de données."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Déconnecte de la base de données."""
        pass

    @abstractmethod
    def get_table(self, table_name: str) -> TableMetaData:
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


class SQLite(Database[TABLE_ORM_TYPE]):
    """
    Représente une base de données SQLite.
    """

    class TableMetaData(Database.TableMetaData):
        """
        Métadonnées d'une table SQLite.
        """

        pass

    def __init__(self, db_config: Path) -> None:
        """
        Constructeur de la base de données SQLite.

        :param db_config: Configuration de la base de données.
        """
        super().__init__(db_config)

    def connect(self) -> Any:
        """Connecte à la base de données SQLite."""
        raise NotImplementedError

    def disconnect(self) -> None:
        """Déconnecte de la base de données SQLite."""
        raise NotImplementedError

    def get_table(self, table_name: str) -> SQLite.TableMetaData:
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


class PostgreSQL(Database[TABLE_ORM_TYPE]):
    """
    Représente une base de données PostgreSQL.
    """

    def __init__(self, db_config: DbConfig) -> None:
        """
        Constructeur de la base de données PostgreSQL.

        :param db_config: Configuration de la base de données.
        """
        super().__init__(db_config)

    def connect(self) -> Any:
        """Connecte à la base de données PostgreSQL."""
        raise NotImplementedError

    def disconnect(self) -> None:
        """Déconnecte de la base de données PostgreSQL."""
        raise NotImplementedError

    def get_table(self, table_name: str) -> PostgreSQL.TableMetaData:
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


class MySQL(Database[TABLE_ORM_TYPE]):
    """
    Représente une base de données MySQL.
    """

    def __init__(self, db_config: DbConfig) -> None:
        """
        Constructeur de la base de données MySQL.

        :param db_config: Configuration de la base de données.
        """
        super().__init__(db_config)

    def connect(self) -> Any:
        """Connecte à la base de données MySQL."""
        raise NotImplementedError

    def disconnect(self) -> None:
        """Déconnecte de la base de données MySQL."""
        raise NotImplementedError

    def get_table(self, table_name: str) -> MySQL.TableMetaData:
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


class OracleDB(Database[TABLE_ORM_TYPE]):
    """
    Représente une base de données Oracle.
    """

    def __init__(self, db_config: DbConfig) -> None:
        """
        Constructeur de la base de données Oracle.

        :param db_config: Configuration de la base de données.
        """
        super().__init__(db_config)

    def connect(self) -> Any:
        """Connecte à la base de données Oracle."""
        raise NotImplementedError

    def disconnect(self) -> None:
        """Déconnecte de la base de données Oracle."""
        raise NotImplementedError

    def get_table(self, table_name: str) -> OracleDB.TableMetaData:
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


class SQLServer(Database[TABLE_ORM_TYPE]):
    """
    Représente une base de données SQL Server.
    """

    def __init__(self, db_config: DbConfig) -> None:
        """
        Constructeur de la base de données SQL Server.

        :param db_config: Configuration de la base de données.
        """
        super().__init__(db_config)

    def connect(self) -> Any:
        """Connecte à la base de données SQL Server."""
        raise NotImplementedError

    def disconnect(self) -> None:
        """Déconnecte de la base de données SQL Server."""
        raise NotImplementedError

    def get_table(self, table_name: str) -> SQLServer.TableMetaData:
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


class Table(Generic[TABLE_ORM_TYPE]):
    """
    Représente une table de la base de données.

    :param name: Nom de la table.
    :param database: Base de données à laquelle appartient la table.
    :param columns: Colonnes de la table.
    """

    db_name: str
    vb_name: str
    database: Database[TABLE_ORM_TYPE]
    columns: list[Column]
    link_table: Type[ORM.Table]

    def __init__(self, name: str, database: Database[TABLE_ORM_TYPE]) -> None:
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

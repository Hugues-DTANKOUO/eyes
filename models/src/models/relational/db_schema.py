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
    - ForeignKeyColumn: Colonne de clé étrangère.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Generic, TypeVar, Type, cast, Sequence
from abc import ABC, abstractmethod
import json

from models.relational.orm import ORM
from models.relational.config import DbConfig, DataBaseType
from models.relational.metadata import (
    ColumnMeta,
    ColumnType,
    ForeignKeyColumnMeta,
    ForeignKeyAction,
    UniqueColumnsMeta,
    DatabaseMetaDict,
)


ORM_TYPE = TypeVar("ORM_TYPE", bound=ORM)
TABLE_ORM_TYPE = TypeVar("TABLE_ORM_TYPE", bound=ORM.Table)
COLUMN_ORM_TYPE = TypeVar("COLUMN_ORM_TYPE", bound=ORM.Column)
FOREIGNKEY_COLUMN_ORM_TYPE = TypeVar(
    "FOREIGNKEY_COLUMN_ORM_TYPE", bound=ORM.ForeignKeyColumn
)


class Database(Generic[ORM_TYPE, TABLE_ORM_TYPE], ABC):
    """
    Classe abstraite représentant une base de données.

    :param _name: Nom de la base de données.
    :param _type: Type de la base de données.
    :param _orm: Couche ORM de la base de données.
    :param tables: Tables de la base de données.
    """

    _name: str
    _type: DataBaseType
    _orm: ORM_TYPE
    tables: dict[str, Type[TABLE_ORM_TYPE]]
    _schema: str | None = None

    def __init__(self, db_config: DbConfig | Path, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Constructeur de la base de données.

        :param db_config: Configuration de la base de données.
        :param orm_class_: Classe de la couche ORM.
        """

        if isinstance(db_config, DbConfig):
            engine_url = db_config.get_engine_url()
            self._type = db_config.type
            self._name = db_config.database
            self._schema = db_config.db_schema
        elif isinstance(db_config, Path):
            if db_config.suffix == ".db":
                engine_url = "sqlite:///" + str(db_config)
                self._type = DataBaseType.SQLITE
                self._name = db_config.stem
            else:
                raise ValueError("Le type de base de données n'est pas supporté.")
        else:
            raise ValueError("La configuration de la base de données est invalide.")
        self._orm = orm_class_(engine_url, self._schema)
        self._get_orm_tables()

    @property
    def name(self) -> str:
        """Retourne le nom de la base de données."""
        return self._name

    @name.setter
    def name(self, _: str) -> None:
        """Définit le nom de la base de données."""
        raise AttributeError("Impossible de modifier le nom de la base de données.")

    def disconnection(self) -> None:
        """Déconnecte de la base de données."""
        self._orm.close_session()

    def get_orm_table(self, table_name: str) -> Type[TABLE_ORM_TYPE]:
        """
        Récupère une table du type de la couche ORM.

        :param table_name: Nom de la table.
        :return: Table.
        """
        try:
            return cast(Type[TABLE_ORM_TYPE], self._orm.get_table(table_name))
        except self._orm.NoSuchTableError as e:
            raise self._orm.NoSuchTableError(e) from e
        except Exception as e:
            raise Exception(f"Impossible de récupérer la table {table_name}.") from e

    def _get_orm_tables(self) -> None:
        """
        Récupère les tables du type de la couche ORM.
        """
        try:
            self.tables = {
                table_name: cast(Type[TABLE_ORM_TYPE], table)
                for table_name, table in self._orm.get_tables().items()
            }
        except Exception as e:
            raise Exception("Impossible de récupérer les tables.") from e

    def refresh(self) -> None:
        """
        Rafraîchit les tables de la base de données.
        """
        self._get_orm_tables()

    def create_orm_table(
        self,
        table_name: str,
        columns: list[ColumnMeta | ForeignKeyColumnMeta],
        unique_constraints_columns: list[UniqueColumnsMeta] | None = None,
    ) -> Type[TABLE_ORM_TYPE]:
        """
        Récupère ou crée une table du type de la couche ORM.
        :param table_name: Nom de la table.
        :param columns: Colonnes de la table.
        :param unique_constraints_columns: Contraintes d'unicité.
        :return: Table.
        """

        try:
            table = cast(
                Type[TABLE_ORM_TYPE],
                self._orm.create_table(table_name, columns, unique_constraints_columns),
            )
            self.tables[table_name] = table
            return table
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

    def get_schema(self) -> DatabaseMetaDict:
        """
        Récupère le schéma de la base de données.

        :return: Schéma de la base de données.
        """

        self._get_orm_tables()
        return {
            "name": self._name,
            "type": self._type.value,
            "tables": {
                table_name: {
                    "name": table_name,
                    "columns": {
                        column.meta.name: column.meta.get_dict()
                        for column in table.columns
                    },
                    "unique_columns": {
                        unique.name: unique.columns
                        for unique in table.unique_constraints
                    },
                }
                for table_name, table in self.tables.items()
            },
        }

    def save_schema(self, path: Path) -> None:
        """
        Enregistre le schéma de la base de données dans un fichier JSON.

        :param path: Chemin du fichier JSON.
        """
        with open(path, "w", encoding="latin1") as file:
            json.dump(self.get_schema(), file, indent=4)


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


class Table(
    Generic[ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE]
):
    """
    Représente une table de la base de données.

    :param name: Nom de la table.
    :param database: Base de données à laquelle appartient la table.
    :param columns: Colonnes de la table.
    :param unique_contraints_columns: Liste des contraintes d'unicité.
    """

    _db_name: str
    vb_name: str
    database: Database[ORM_TYPE, TABLE_ORM_TYPE]
    _columns: list[
        Column[ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE]
        | ForeignKeyColumn[
            ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE
        ]
    ]
    _unique_constraints_columns: list[UniqueConstraint]
    link_table: Type[TABLE_ORM_TYPE]

    def __init__(
        self,
        name: str,
        database: Database[ORM_TYPE, TABLE_ORM_TYPE],
        columns: list[ColumnMeta | ForeignKeyColumnMeta] | None = None,
        unique_constraints_columns: list[UniqueColumnsMeta] | None = None,
    ) -> None:
        """
        Constructeur de la table.

        :param name: Nom de la table.
        :param database: Base de données à laquelle appartient la table.
        :param columns: Colonnes de la table.
        :param unique_constraints_columns: Contraintes d'unicité.
        """

        try:
            if columns is not None:
                if name in database.tables:
                    table = database.tables[name]
                else:
                    table = database.create_orm_table(
                        name, columns, unique_constraints_columns
                    )
            else:
                table = database.get_orm_table(name)
            self._db_name = table.name  # type: ignore
            self.vb_name = name
            self.database = database
            self._link_table = table
            self._columns = [
                (
                    ForeignKeyColumn[
                        ORM_TYPE,
                        TABLE_ORM_TYPE,
                        COLUMN_ORM_TYPE,
                        FOREIGNKEY_COLUMN_ORM_TYPE,
                    ](column.meta, self)
                    if isinstance(column.meta, ForeignKeyColumnMeta)
                    else Column[
                        ORM_TYPE,
                        TABLE_ORM_TYPE,
                        COLUMN_ORM_TYPE,
                        FOREIGNKEY_COLUMN_ORM_TYPE,
                    ](column.meta, self)
                )
                for column in table.columns
            ]
            self._unique_constraints_columns = [
                UniqueConstraint(unique, self) for unique in table.unique_constraints
            ]
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
    def primary_key(
        self,
    ) -> Column[ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE]:
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
    def columns(
        self,
    ) -> list[
        Column[ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE]
        | ForeignKeyColumn[
            ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE
        ]
    ]:
        """Retourne les colonnes de la table."""
        return self._columns

    @property
    def unique_columns(self) -> list[UniqueConstraint]:
        """Retourne les contraintes d'unicité de la table."""
        return self._unique_constraints_columns

    @property
    def db_name(self) -> str:
        """Retourne le nom de la table dans la base de données."""
        return self._db_name

    @db_name.setter
    def db_name(self, name: str) -> None:
        """
        Modifie le nom de la table dans la base de données.
        :param name: Nom de la table.
        """
        self._link_table.name = name  # type: ignore
        self._link_table = self.database.get_orm_table(name)
        self._db_name = name

    def refresh(self) -> None:
        """
        Rafraîchit les données de la table.
        """
        self._link_table = self.database.get_orm_table(self.vb_name)
        self._columns = [
            (
                ForeignKeyColumn(column.meta, self)
                if isinstance(column.meta, ForeignKeyColumnMeta)
                else Column(column.meta, self)
            )
            for column in self._link_table.columns
        ]
        self._unique_constraints_columns = [
            UniqueConstraint(unique, self)
            for unique in self._link_table.unique_constraints
        ]

    def get_column(
        self, column_name: str
    ) -> (
        Column[ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE]
        | ForeignKeyColumn[
            ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE
        ]
    ):
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

    def add_column(
        self, column_meta: ColumnMeta | ForeignKeyColumnMeta
    ) -> (
        Column[ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE]
        | ForeignKeyColumn[
            ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE
        ]
    ):
        """
        Ajoute une colonne à la table.

        :param column: Métadonnées de la colonne.
        :return: Colonne.
        """
        column_orm_meta = cast(
            Type[COLUMN_ORM_TYPE | FOREIGNKEY_COLUMN_ORM_TYPE], self._link_table.add_column(column_meta)  # type: ignore
        ).meta
        self.refresh()
        column = (
            ForeignKeyColumn(meta_data=column_orm_meta, table=self)
            if isinstance(column_orm_meta, ForeignKeyColumnMeta)
            else Column(meta_data=column_orm_meta, table=self)
        )
        return column


class Column(
    Generic[ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE]
):
    """
    Représente une colonne d'une table.

    :param name: Nom de la colonne.
    :param type: Type de la colonne.
    :param length: Longueur de la colonne.
    :param nullable: Indique si la colonne peut être nulle.
    :param primary_key: Indique si la colonne est une clé primaire.
    :param default: Valeur par défaut de la colonne.
    :param unique: Indique si la colonne est unique.
    :param table: Table à laquelle appartient la colonne.
    """

    _name: str
    type: ColumnType
    length: int | None
    nullable: bool
    primary_key: bool
    default: Any | None
    unique: bool
    table: Table[ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE]
    link_column: Type[COLUMN_ORM_TYPE | FOREIGNKEY_COLUMN_ORM_TYPE]

    def __init__(
        self,
        meta_data: ColumnMeta,
        table: Table[
            ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE
        ],
    ) -> None:
        """
        Constructeur de la colonne.

        :param meta_data: Métadonnées de la colonne.
        :param table: Table à laquelle appartient la colonne.
        """
        self._name = meta_data.name
        self.type = meta_data.type
        self.length = meta_data.length
        self.nullable = meta_data.nullable
        self.primary_key = meta_data.primary_key
        self.default = meta_data.default
        self.unique = meta_data.unique
        self.table = table
        self._link_column = cast(
            Type[COLUMN_ORM_TYPE | FOREIGNKEY_COLUMN_ORM_TYPE],
            next(
                column
                for column in table._link_table.columns
                if column.meta.name == self._name
            ),
        )

    def __str__(self) -> str:
        """Retourne une représentation de la colonne."""
        return f"Colonne {self.name} de type {self.type.value} de la table {self.table.vb_name}"

    @property
    def name(self) -> str:
        """
        Retourne le nom de la colonne.

        :return: Nom de la colonne.
        """
        return self._name

    @name.setter
    def name(self, column_name: str) -> None:
        """
        Modifie le nom de la colonne.

        :param column_name: Nom de la colonne.
        """
        self._link_column = cast(
            Type[COLUMN_ORM_TYPE | FOREIGNKEY_COLUMN_ORM_TYPE],
            self._link_column.set_name(column_name),  # type: ignore
        )
        self._name = column_name
        self.table.refresh()


class ForeignKeyColumn(
    Column[ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE]
):
    """
    Représente une colonne de clé étrangère.

    :param name: Nom de la colonne.
    :param type: Type de la colonne.
    :param length: Longueur de la colonne.
    :param nullable: Indique si la colonne peut être nulle.
    :param primary_key: Indique si la colonne est une clé primaire.
    :param default: Valeur par défaut de la colonne.
    :param table: Table à laquelle appartient la colonne.
    :param foreign_table: Table étrangère.
    :param foreign_column: Colonne étrangère.
    :param on_delete: Action sur suppression.
    :param on_update: Action sur mise à jour.
    """

    foreign_table: Table[
        ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE
    ]
    foreign_column: Column[
        ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE
    ]
    on_delete: ForeignKeyAction = ForeignKeyAction.NO_ACTION
    on_update: ForeignKeyAction = ForeignKeyAction.NO_ACTION

    def __init__(
        self,
        meta_data: ForeignKeyColumnMeta,
        table: Table[
            ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE
        ],
    ) -> None:
        """
        Constructeur de la colonne de clé étrangère.

        :param meta_data: Métadonnées de la colonne.
        :param table: Table à laquelle appartient la colonne.
        """
        super().__init__(meta_data, table)
        self.foreign_table = Table(meta_data.foreign_table_name, table.database)
        self.foreign_column = self.foreign_table.get_column(
            meta_data.foreign_column_name
        )
        self.on_delete = meta_data.on_delete
        self.on_update = meta_data.on_update

    def __str__(self) -> str:
        """Retourne une représentation de la colonne de clé étrangère."""
        return (
            f"Colonne {self.name} de type {self.type.value} de la table"
            f" {self.table.vb_name} avec clé étrangère vers la table {self.foreign_table.vb_name}"
        )


class UniqueConstraint:
    """
    Représente une contrainte d'unicité sur une table.

    :param name: Nom de la contrainte d'unicité.
    :param table: Table à laquelle appartient la contrainte d'unicité.
    :param columns: Colonnes de la contrainte d'unicité.
    """

    name: str
    table: Table
    columns: Sequence[Column | ForeignKeyColumn]

    def __init__(self, meta_data: UniqueColumnsMeta, table: Table) -> None:
        """
        Constructeur de la contrainte d'unicité.

        :param meta_data: Métadonnées de la contrainte d'unicité.
        :param table: Table à laquelle appartient la contrainte d'unicité.
        """

        self.name = meta_data.name
        self.table = table
        self.columns = [
            table.get_column(column_name) for column_name in meta_data.columns
        ]

    def __str__(self) -> str:
        """Retourne une représentation de la contrainte d'unicité."""
        return (
            f"Contrainte d'unicité {self.name} sur la table {self.table.vb_name} pour les colonnes : "
            + ", ".join(column.name for column in self.columns)
        )

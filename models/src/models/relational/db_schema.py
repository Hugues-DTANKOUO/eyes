"""
Base structure for a relational data model.

- Classes:
    - Database: Database.
    - SQLite: SQLite database.
    - PostgreSQL: PostgreSQL database.
    - MySQL: MySQL database.
    - OracleDB: Oracle database.
    - SQLServer: SQL Server database.
    - Table: Database table.
    - Column: Table column.
    - ForeignKeyColumn: Foreign key column.
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
    Abstract class representing a database.

    :param _name: Database name.
    :param _type: Database type.
    :param _orm: Database ORM layer.
    :param tables: Database tables.
    """

    _name: str
    _type: DataBaseType
    _orm: ORM_TYPE
    tables: dict[str, Type[TABLE_ORM_TYPE]]
    _schema: str | None = None

    def __init__(self, db_config: DbConfig | Path, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Database constructor.

        :param db_config: Database configuration.
        :param orm_class_: ORM layer class.
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
                raise ValueError("Database type is not supported.")
        else:
            raise ValueError("Invalid database configuration.")
        self._orm = orm_class_(engine_url, self._schema)
        self._get_orm_tables()

    @property
    def name(self) -> str:
        """Returns the database name."""
        return self._name

    @name.setter
    def name(self, _: str) -> None:
        """Sets the database name."""
        raise AttributeError("Cannot modify database name.")

    def disconnection(self) -> None:
        """Disconnects from the database."""
        self._orm.close_session()

    def get_orm_table(self, table_name: str) -> Type[TABLE_ORM_TYPE]:
        """
        Gets a table of ORM layer type.

        :param table_name: Table name.
        :return: Table.
        """
        try:
            return cast(Type[TABLE_ORM_TYPE], self._orm.get_table(table_name))
        except self._orm.NoSuchTableError as e:
            raise self._orm.NoSuchTableError(e) from e
        except Exception as e:
            raise Exception(f"Cannot get table {table_name}.") from e

    def _get_orm_tables(self) -> None:
        """
        Gets tables of ORM layer type.
        """
        try:
            self.tables = {
                table_name: cast(Type[TABLE_ORM_TYPE], table)
                for table_name, table in self._orm.get_tables().items()
            }
        except Exception as e:
            raise Exception("Cannot get tables.") from e

    def refresh(self) -> None:
        """
        Refreshes database tables.
        """
        self._get_orm_tables()

    def create_orm_table(
        self,
        table_name: str,
        columns: list[ColumnMeta | ForeignKeyColumnMeta],
        unique_constraints_columns: list[UniqueColumnsMeta] | None = None,
    ) -> Type[TABLE_ORM_TYPE]:
        """
        Gets or creates a table of ORM layer type.
        :param table_name: Table name.
        :param columns: Table columns.
        :param unique_constraints_columns: Unique constraints.
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
            raise Exception(f"Cannot get or create table {table_name}.") from e

    @abstractmethod
    def execute(self, query: str) -> Any:
        """
        Executes a query on the database.

        :param query: Query to execute.
        :return: Query result.
        """
        pass

    def get_schema(self) -> DatabaseMetaDict:
        """
        Gets the database schema.

        :return: Database schema.
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
        Saves the database schema to a JSON file.

        :param path: JSON file path.
        """
        with open(path, "w", encoding="latin1") as file:
            json.dump(self.get_schema(), file, indent=4)


class SQLite(Database[ORM_TYPE, TABLE_ORM_TYPE]):
    """
    Represents a SQLite database.
    """

    def __init__(self, db_config: Path, orm_class_: Type[ORM_TYPE]) -> None:
        """
        SQLite database constructor.

        :param db_config: Database configuration.
        :param orm_class_: ORM layer class.
        """
        super().__init__(db_config, orm_class_)

    def execute(self, query: str) -> Any:
        """
        Executes a query on the SQLite database.

        :param query: Query to execute.
        :return: Query result.
        """
        pass


class PostgreSQL(Database[ORM_TYPE, TABLE_ORM_TYPE]):
    """
    Represents a PostgreSQL database.
    """

    def __init__(self, db_config: DbConfig, orm_class_: Type[ORM_TYPE]) -> None:
        """
        PostgreSQL database constructor.

        :param db_config: Database configuration.
        :param orm_class_: ORM layer class.
        """
        super().__init__(db_config, orm_class_)

    def execute(self, query: str) -> Any:
        """
        Executes a query on the PostgreSQL database.

        :param query: Query to execute.
        :return: Query result.
        """
        pass


class MySQL(Database[ORM_TYPE, TABLE_ORM_TYPE]):
    """
    Represents a MySQL database.
    """

    def __init__(self, db_config: DbConfig, orm_class_: Type[ORM_TYPE]) -> None:
        """
        MySQL database constructor.

        :param db_config: Database configuration.
        :param orm_class_: ORM layer class.
        """
        super().__init__(db_config, orm_class_)

    def execute(self, query: str) -> Any:
        """
        Executes a query on the MySQL database.

        :param query: Query to execute.
        :return: Query result.
        """
        pass


class OracleDB(Database[ORM_TYPE, TABLE_ORM_TYPE]):
    """
    Represents an Oracle database.
    """

    def __init__(self, db_config: DbConfig, orm_class_: Type[ORM_TYPE]) -> None:
        """
        Oracle database constructor.

        :param db_config: Database configuration.
        :param orm_class_: ORM layer class.
        """
        super().__init__(db_config, orm_class_)

    def execute(self, query: str) -> Any:
        """
        Executes a query on the Oracle database.

        :param query: Query to execute.
        :return: Query result.
        """
        pass


class SQLServer(Database[ORM_TYPE, TABLE_ORM_TYPE]):
    """
    Represents a SQL Server database.
    """

    def __init__(self, db_config: DbConfig, orm_class_: Type[ORM_TYPE]) -> None:
        """
        SQL Server database constructor.

        :param db_config: Database configuration.
        """
        super().__init__(db_config, orm_class_)

    def execute(self, query: str) -> Any:
        """
        Executes a query on the SQL Server database.

        :param query: Query to execute.
        :return: Query result.
        """
        pass


class Table(
    Generic[ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE]
):
    """
    Represents a database table.

    :param name: Table name.
    :param database: Database containing the table.
    :param columns: Table columns.
    :param unique_constraints_columns: List of unique constraints.
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
        Table constructor.

        :param name: Table name.
        :param database: Database containing the table.
        :param columns: Table columns.
        :param unique_constraints_columns: Unique constraints.
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
            raise Exception(f"Error while creating table {name}.") from e

    def __str__(self) -> str:
        """Returns a string representation of the table."""
        return f"Table {self.vb_name} from database {self.database.name}"

    @property
    def name(self) -> str:
        """Returns the table name."""
        return self.vb_name

    @property
    def primary_key(
        self,
    ) -> Column[ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE]:
        """
        Returns the table's primary key column.

        :return: Primary key column.
        """
        for column in self._columns:
            if column.primary_key:
                return column
        raise ValueError(f"No primary key column exists in table {self.vb_name}.")

    @property
    def columns(
        self,
    ) -> list[
        Column[ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE]
        | ForeignKeyColumn[
            ORM_TYPE, TABLE_ORM_TYPE, COLUMN_ORM_TYPE, FOREIGNKEY_COLUMN_ORM_TYPE
        ]
    ]:
        """Returns the table columns."""
        return self._columns

    @property
    def unique_columns(self) -> list[UniqueConstraint]:
        """Returns the table's unique constraints."""
        return self._unique_constraints_columns

    @property
    def db_name(self) -> str:
        """Returns the table name in the database."""
        return self._db_name

    @db_name.setter
    def db_name(self, name: str) -> None:
        """
        Changes the table name in the database.
        :param name: Table name.
        """
        self._link_table.name = name  # type: ignore
        self._link_table = self.database.get_orm_table(name)
        self._db_name = name

    def refresh(self) -> None:
        """
        Refreshes table data.
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
        Returns a column from the table.

        :param column_name: Column name.
        :return: Column.
        """
        for column in self._columns:
            if column.name == column_name:
                return column
        raise ValueError(
            f"Column {column_name} does not exist in table {self.vb_name}."
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
        Adds a column to the table.

        :param column: Column metadata.
        :return: Column.
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
    Represents a table column.

    :param name: Column name.
    :param type: Column type.
    :param length: Column length.
    :param nullable: Indicates if the column can be null.
    :param primary_key: Indicates if the column is a primary key.
    :param default: Column default value.
    :param unique: Indicates if the column is unique.
    :param table: Table containing the column.
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
        Column constructor.

        :param meta_data: Column metadata.
        :param table: Table containing the column.
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
        """Returns a string representation of the column."""
        return f"Column {self.name} of type {self.type.value} from table {self.table.vb_name}"

    @property
    def name(self) -> str:
        """
        Returns the column name.

        :return: Column name.
        """
        return self._name

    @name.setter
    def name(self, column_name: str) -> None:
        """
        Changes the column name.

        :param column_name: Column name.
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
    Represents a foreign key column.

    :param name: Column name.
    :param type: Column type.
    :param length: Column length.
    :param nullable: Indicates if the column can be null.
    :param primary_key: Indicates if the column is a primary key.
    :param default: Column default value.
    :param table: Table containing the column.
    :param foreign_table: Referenced table.
    :param foreign_column: Referenced column.
    :param on_delete: Action on delete.
    :param on_update: Action on update.
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
        Foreign key column constructor.

        :param meta_data: Column metadata.
        :param table: Table containing the column.
        """
        super().__init__(meta_data, table)
        self.foreign_table = Table(meta_data.foreign_table_name, table.database)
        self.foreign_column = self.foreign_table.get_column(
            meta_data.foreign_column_name
        )
        self.on_delete = meta_data.on_delete
        self.on_update = meta_data.on_update

    def __str__(self) -> str:
        """Returns a string representation of the foreign key column."""
        return (
            f"Column {self.name} of type {self.type.value} from table"
            f" {self.table.vb_name} with foreign key to table {self.foreign_table.vb_name}"
        )


class UniqueConstraint:
    """
    Represents a table unique constraint.

    :param name: Unique constraint name.
    :param table: Table containing the unique constraint.
    :param columns: Columns in the unique constraint.
    """

    name: str
    table: Table
    columns: Sequence[Column | ForeignKeyColumn]

    def __init__(self, meta_data: UniqueColumnsMeta, table: Table) -> None:
        """
        Unique constraint constructor.

        :param meta_data: Unique constraint metadata.
        :param table: Table containing the unique constraint.
        """

        self.name = meta_data.name
        self.table = table
        self.columns = [
            table.get_column(column_name) for column_name in meta_data.columns
        ]

    def __str__(self) -> str:
        """Returns a string representation of the unique constraint."""
        return (
            f"Unique constraint {self.name} on table {self.table.vb_name} for columns: "
            + ", ".join(column.name for column in self.columns)
        )

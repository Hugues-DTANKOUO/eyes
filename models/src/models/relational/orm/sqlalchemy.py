from __future__ import annotations

from sqlalchemy.engine import Connection, Engine, create_engine
from sqlalchemy.exc import (
    NoSuchTableError as SQLAlchemyNoSuchTableError,
    SQLAlchemyError,
)
from sqlalchemy.schema import (
    Column,
    ForeignKey,
    UniqueConstraint,
    MetaData,
    Table,
    DefaultClause,
)
from sqlalchemy.sql.expression import TextClause
from sqlalchemy.sql import text
from sqlalchemy.types import Integer, String, DateTime, Boolean, Float, Date, Text
from typing import cast, Type, Any

from models.relational.orm import ORM
from models.relational.metadata import (
    ColumnMeta,
    ColumnType,
    ForeignKeyColumnMeta,
    ForeignKeyAction,
    UniqueColumnsMeta,
)


def get_sqlalchemy_type(column_type: ColumnType, column_length: int | None) -> type:
    """
    Returns the SQLAlchemy type corresponding to a column type.
    :param column_type: Column type.
    :param column_length: Column length.
    :return: SQLAlchemy type.
    """

    type_alchemy = {
        ColumnType.INT: cast(type, Integer),
        ColumnType.VARCHAR: cast(type, String),
        ColumnType.TEXT: cast(type, Text),
        ColumnType.DATE: cast(type, Date),
        ColumnType.DATETIME: cast(type, DateTime),
        ColumnType.BOOLEAN: cast(type, Boolean),
        ColumnType.DECIMAL: cast(type, Float),
    }[column_type]
    if column_length is not None and (type_alchemy == String or type_alchemy == Text):
        type_alchemy = cast(type, String(length=column_length))
    return type_alchemy


def cast_to_sqlalchemy_type(
    column_type: ColumnType, column_length: int | None
) -> Integer | String | DateTime | Boolean | Float | Date | Text:
    """
    Converts a column type to SQLAlchemy type.
    :param column_type: Column type.
    :param column_length: Column length.
    :return: SQLAlchemy column type.
    """
    return cast(
        Integer | String | DateTime | Boolean | Float | Date | Text,
        get_sqlalchemy_type(column_type, column_length),
    )


def get_column_type(column_type: type) -> ColumnType:
    """
    Returns the column type corresponding to a SQLAlchemy type.
    :param column_type: SQLAlchemy type.
    :return: Column type.
    """

    column_type_str = str(column_type).split("(")[0]

    return {
        "INTEGER": ColumnType.INT,
        "VARCHAR": ColumnType.VARCHAR,
        "TEXT": ColumnType.TEXT,
        "DATE": ColumnType.DATE,
        "DATETIME": ColumnType.DATETIME,
        "BOOLEAN": ColumnType.BOOLEAN,
        "DECIMAL": ColumnType.DECIMAL,
    }[column_type_str]


def cast_default(default: Any | None, column_type: type) -> Any:
    """
    Converts a column's default value.
    :param default: Default value.
    :param column_type: Column type.
    :return: Converted default value.
    """

    column_type_str = str(column_type).split("(")[0]

    if default is None:
        return None

    try:
        if column_type_str == "INTEGER":
            return int(default)
        elif (
            column_type_str == "VARCHAR"
            or column_type_str == "TEXT"
            or column_type_str == "DATETIME"
            or column_type_str == "DATE"
        ):
            return str(default)
        elif column_type_str == "BOOLEAN":
            return bool(default)
        elif column_type_str == "DECIMAL":
            return float(default)
    except Exception:
        return None


class SQLAlchemy(ORM):
    """
    SQLAlchemy ORM layer management class.

    - Classes:
        - Table: Table management class.
        - Column: Column management class.
        - NoSuchTableError: Table not found error.

    - Attributes:
        - engine: Database connection engine.
        - schema: Database schema/partition.
        - _metadata: Database metadata.
    """

    engine: Engine
    schema: str | None
    _metadata: MetaData

    class Table(ORM.Table):
        """
        Table management class.

        - Attributes:
            - _link_table: Linked table.
            - name: Table name.
            - columns: Table columns.
            - unique_constraints: Unique constraints.
            - orm: ORM instance.
        """

        _link_table: Table
        _name: str
        columns: list[SQLAlchemy.Column | SQLAlchemy.ForeignKeyColumn]
        unique_constraints: list[UniqueColumnsMeta]
        orm: SQLAlchemy

        def __init__(self, table: Table, sql_alchemy_instance: SQLAlchemy) -> None:
            """
            Creates a table.
            :param table: Table to create.
            :param sql_alchemy_instance: SQLAlchemy ORM instance.
            :return: Table.
            """

            self._name = table.name
            self._link_table = table
            self.orm = sql_alchemy_instance

            self.columns = []
            self.unique_constraints = []

            for column in table.columns:
                self.columns.append(
                    SQLAlchemy.ForeignKeyColumn(column, self)
                    if column.foreign_keys
                    else SQLAlchemy.Column(column, self)
                )

            for unique_constraint in table.constraints:
                if (
                    isinstance(unique_constraint, UniqueConstraint)
                    and unique_constraint.columns.__len__()
                ):
                    if unique_constraint.columns.__len__() == 1:
                        for column_alchemy in self.columns:
                            if (
                                column_alchemy.meta.name
                                == next(iter(unique_constraint.columns)).name
                            ):
                                column_alchemy.meta.unique = True
                    else:
                        self.unique_constraints.append(
                            UniqueColumnsMeta(
                                name=str(unique_constraint.name or ""),
                                columns=set(
                                    column.name for column in unique_constraint.columns
                                ),
                            )
                        )

        def add_column(
            self,
            column: ColumnMeta | ForeignKeyColumnMeta,
        ) -> SQLAlchemy.Column | SQLAlchemy.ForeignKeyColumn:
            """
            Adds a column to the table.
            :param column: Column to create.
            :return: Column.
            """

            if self.has_column(column.name):
                raise self.AddColumnError(
                    f"Cannot create column {column.name}.\n"
                    f"Column already exists in table {self.name}."
                )

            with self.orm.engine.connect() as connection:
                try:
                    column_type_compiled = cast_to_sqlalchemy_type(
                        column.type, column.length
                    ).compile(self.orm.engine.dialect)
                    Verbs = SQLAlchemy.SQL_Verbs
                    AlchColumn = SQLAlchemy.Column
                    foreign_table_name = (
                        self._table_name_for_request(column.foreign_table_name)
                        if isinstance(column, ForeignKeyColumnMeta)
                        else ""
                    )
                    alter_statement = text(
                        f"{Verbs.ALTER_TABLE.value} {self._table_name_for_request()} "
                        f"{Verbs.ADD_COLUMN.value} {AlchColumn._name_for_request(column.name)} "
                        f"{column_type_compiled} {AlchColumn._nullable_for_request(column.nullable)} "
                        f"{AlchColumn._default_for_request(column.default)} "
                        f"{AlchColumn._primary_key_for_request(column.primary_key)} "
                        f"{AlchColumn._unique_for_request(column.unique)} "
                        f"{AlchColumn._foreign_key_for_request(column, foreign_table_name)}"
                    )
                    self.orm.execute(connection, alter_statement)
                    self = self.orm.get_table(self.name)
                    return self.get_column(column.name)
                except Exception as e:
                    raise self.AddColumnError(
                        f"Cannot create column {column.name} in table {self.name}."
                    ) from e

        def get_column(
            self, name: str
        ) -> SQLAlchemy.Column | SQLAlchemy.ForeignKeyColumn:
            """
            Gets a column from the table.
            :param name: Column name.
            :return: Column.
            """
            if self.has_column(name):
                column = self._link_table.columns[name]
                if column.foreign_keys:
                    return SQLAlchemy.ForeignKeyColumn(column, self)
                return SQLAlchemy.Column(column, self)
            raise KeyError(f"Column {name} does not exist in table {self.name}.")

        def has_column(self, name: str) -> bool:
            """
            Checks if a column exists in the table.
            :param name: Column name.
            :return: True if the column exists, false otherwise.
            """
            return name in self._link_table.columns

        @property
        def name(self) -> str:
            """
            Returns the table name.
            :return: Table name.
            """

            return self._name

        @name.setter
        def name(self, name: str) -> None:
            """
            Changes the table name.
            :param name: Table name.
            """
            try:
                with self.orm.engine.connect() as connection:
                    alter_statement = text(
                        f"{SQLAlchemy.SQL_Verbs.ALTER_TABLE.value} "
                        f"{self._table_name_for_request()} "
                        f'{SQLAlchemy.SQL_Verbs.RENAME_TO.value} "{name}"'
                    )
                    self.orm.execute(connection, alter_statement)
                    self = self.orm.get_table(name)
            except SQLAlchemyError as e:
                raise self.orm.SQLExecutionError(
                    f"Cannot rename table {self._name} to {name}."
                ) from e

    class Column(ORM.Column):
        """
        Column management class.
        """

        meta: ColumnMeta
        _link_column: Column
        table: SQLAlchemy.Table

        def __init__(self, column: Column, table: SQLAlchemy.Table) -> None:
            """
            Creates a column.
            :param column: Column to create.
            :param table: Column's table.
            :return: Column.
            """

            self._link_column = column

            name = column.name
            type_column = get_column_type(cast(type, column.type))
            length = int(getattr(column.type, "length", None) or 0) or None
            nullable = column.nullable or False
            primary_key = column.primary_key
            unique = column.unique or False
            default = (
                cast_default(
                    getattr(
                        column.server_default.arg, "text", column.server_default.arg
                    ),
                    cast(type, column.type),
                )
                if isinstance(column.server_default, DefaultClause)
                else None
            )
            self.meta = ColumnMeta(
                name=name,
                type=type_column,
                length=length,
                nullable=nullable,
                primary_key=primary_key,
                unique=unique,
                default=default,
            )
            self.table = table

        def set_name(self, name: str) -> SQLAlchemy.Column:
            """
            Changes the column name.
            :param name: Column name.
            :return: Column.
            """
            try:
                with self.table.orm.engine.connect() as connection:
                    alter_statement = text(
                        f"{SQLAlchemy.SQL_Verbs.ALTER_TABLE.value} "
                        f"{self.table._table_name_for_request()}"
                        f"{SQLAlchemy.SQL_Verbs.RENAME_COLUMN.value} "
                        f"{SQLAlchemy.Column._name_for_request(self.meta.name)} "
                        f"{SQLAlchemy.SQL_Verbs.TO.value} "
                        f"{SQLAlchemy.Column._name_for_request(name)}"
                    )
                    self.table.orm.execute(connection, alter_statement)
                    table = self.table.orm.get_table(self.table.name)
                    self = cast(SQLAlchemy.Column, table.get_column(name))
                    return self
            except SQLAlchemyError as e:
                raise self.orm.SQLExecutionError(
                    f"Cannot rename column {self._link_column.name} to {name}."
                ) from e

    class ForeignKeyColumn(ORM.ForeignKeyColumn):
        """
        Foreign key column management class.
        """

        _link_column: Column
        table: SQLAlchemy.Table

        def __init__(self, column: Column, table: SQLAlchemy.Table) -> None:
            """
            Creates a column.
            :param column: Column to create.
            :param table: Column's table.
            :return: Column.
            """

            foreign_key = next(iter(column.foreign_keys))

            self._link_column = column

            name = column.name
            type_column = get_column_type(cast(type, column.type))
            length = int(getattr(column.type, "length", None) or 0) or None
            nullable = column.nullable or False
            primary_key = column.primary_key
            unique = column.unique or False
            default = (
                cast_default(
                    getattr(
                        column.server_default.arg, "text", column.server_default.arg
                    ),
                    cast(type, column.type),
                )
                if isinstance(column.server_default, DefaultClause)
                else None
            )
            foreign_table_name = foreign_key.column.table.name
            foreign_column_name = foreign_key.column.name
            on_delete = ForeignKeyAction.create(foreign_key.ondelete or "")
            on_update = ForeignKeyAction.create(foreign_key.onupdate or "")

            self.meta = ForeignKeyColumnMeta(
                name=name,
                type=type_column,
                length=length,
                nullable=nullable,
                primary_key=primary_key,
                unique=unique,
                default=default,
                foreign_table_name=foreign_table_name,
                foreign_column_name=foreign_column_name,
                on_delete=on_delete,
                on_update=on_update,
            )
            self.table = table

        def set_name(self, name: str) -> SQLAlchemy.ForeignKeyColumn:
            """
            Changes the column name.
            :param name: Column name.
            :return: Column.
            """
            return cast(SQLAlchemy.ForeignKeyColumn, super().set_name(name))  # type: ignore

    class UniqueConstraint(ORM.UniqueConstraint):
        """
        Unique constraint management class.
        """

        link_constraint: UniqueConstraint

        def __init__(self, constraint: UniqueConstraint) -> None:
            """
            Creates a unique constraint.
            :param constraint: Unique constraint to create.
            :return: Unique constraint.
            """

            self.link_constraint = constraint
            self.name = str(constraint.name or "")
            self.columns = set(column.name for column in constraint.columns)

    class NoSuchTableError(SQLAlchemyNoSuchTableError):
        """
        Table not found error.
        """

        pass

    def __init__(self, engine_url: str, schema: str) -> None:
        """
        SQLAlchemy ORM layer constructor.
        :param engine_url: Database connection URL.
        :param schema: Database schema/partition.
        """

        self.engine = create_engine(engine_url)
        self.schema = schema or None
        self._metadata = MetaData(schema=schema)
        self._metadata.reflect(bind=self.engine)

    def create_table(
        self,
        table_name: str,
        columns: list[ColumnMeta | ForeignKeyColumnMeta],
        unique_constraints_columns: list[UniqueColumnsMeta] | None = None,
    ) -> SQLAlchemy.Table:
        """
        Gets or creates a table.
        :param table_name: Table name.
        :param columns: Table columns.
        :param unique_constraints_columns: Unique constraints.
        :return: Table.
        """
        try:
            has_primary_key = False
            for column in columns:
                if column.primary_key:
                    has_primary_key = True
                    break
            if not has_primary_key:
                raise self.CreateTableError(
                    f"Cannot create table {table_name}.\n"
                    "No primary key column specified."
                )
            table = Table(
                table_name,
                self._metadata,
                *[
                    (
                        Column(
                            column.name,
                            get_sqlalchemy_type(column.type, column.length),
                            ForeignKey(
                                column.foreign_table_name
                                + "."
                                + column.foreign_column_name,
                                ondelete=column.on_delete.value,
                                onupdate=column.on_update.value,
                            ),
                            nullable=column.nullable,
                            primary_key=column.primary_key,
                            unique=column.unique,
                            server_default=column.default,
                        )
                        if isinstance(column, ForeignKeyColumnMeta)
                        else Column(
                            column.name,
                            get_sqlalchemy_type(column.type, column.length),
                            nullable=column.nullable,
                            primary_key=column.primary_key,
                            unique=column.unique,
                            server_default=column.default,
                        )
                    )
                    for column in columns
                ],
                *[
                    UniqueConstraint(
                        *[
                            column.name
                            for column in columns
                            if column.name in unique_constraint.columns
                        ],
                        name=unique_constraint.name,
                    )
                    for unique_constraint in (unique_constraints_columns or [])
                ],
                extend_existing=True,
            )
            table.create(bind=self.engine, checkfirst=True)
            return self.Table(table, self)
        except Exception as e:
            raise self.CreateTableError(f"Cannot create table {table_name}.") from e

    def get_tables(self) -> dict[str, ORM.Table]:
        """
        Gets all database tables.
        :return: Tables.
        """

        return {
            table_name: self.Table(table, self)
            for table_name, table in self._metadata.tables.items()
        }

    def get_table(self, table_name: str) -> SQLAlchemy.Table:
        """
        Gets a database table.
        :param table_name: Table name.
        :return: Table.
        """
        table_name = f"{self.schema}.{table_name}" if self.schema else table_name
        if table_name not in self._metadata.tables:
            raise self.NoSuchTableError(f"Table {table_name} does not exist.")
        return self.Table(self._metadata.tables[table_name], self)

    @staticmethod
    def get_no_such_table_error() -> Type[SQLAlchemyNoSuchTableError]:
        """
        Returns the table not found error.
        :return: Table not found error.
        """

        return SQLAlchemyNoSuchTableError

    def refresh_metadata(self) -> None:
        """
        Refreshes database metadata.
        """
        self._metadata = MetaData(schema=self.schema)
        self._metadata.reflect(bind=self.engine)

    def execute(self, connection: Connection, statement: TextClause) -> None:
        """
        Executes an SQL query.
        :param connection: Database connection.
        :param statement: SQL query.
        """
        connection.execute(statement)
        connection.commit()
        self.refresh_metadata()

    def close_session(self) -> None:
        """Closes database connection."""
        self.engine.dispose()

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
    Base class for ORM layer management.

    - Classes:
        - Table: Table management class.
        - Column: Column management class.
        - NoSuchTableError: Table not found error.
    """

    schema: str | None

    class SQL_Verbs(str, Enum):
        """
        SQL verbs.
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
        Table management class.

        - Attributes:
            - name: Table name.
            - link_table: ORM table.
            - columns_meta: Column metadata.
            - unique_constraints: Unique constraints.
            - orm: ORM instance.
        """

        _name: str
        _link_table: Any
        columns: list[ORM.Column | ORM.ForeignKeyColumn]
        unique_constraints: list[UniqueColumnsMeta]
        orm: ORM

        class AddColumnError(Exception):
            """
            Column addition error.
            """

            pass

        @abstractmethod
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """
            Table class constructor.

            :param *args: Arguments.
            :param **kwargs: Named arguments.
            """

            pass

        @abstractmethod
        def add_column(
            self,
            column: ColumnMeta | ForeignKeyColumnMeta,
        ) -> ORM.Column:
            """
            Adds a column to the table.

            :param column: Column to create.
            :return: Column.
            """

            pass

        @abstractmethod
        def get_column(self, name: str) -> ORM.Column | ORM.ForeignKeyColumn:
            """
            Gets a column from the table.

            :param name: Column name.
            :return: Column.
            """

            pass

        @property
        @abstractmethod
        def name(self) -> str:
            """
            Returns the table name.

            :return: Table name.
            """

            pass

        @name.setter
        @abstractmethod
        def name(self, name: str) -> None:
            """
            Changes the table name.

            :param name: Table name.
            """

            pass

        def _table_name_for_request(self, name: str | None = None) -> str:
            """
            Returns the table name for an SQL request.

            :param name: Table name.
            :return: Table name for SQL request.
            """
            name = name or self.name
            return f'{self.orm.schema}."{name}"' if self.orm.schema else name

    class Column(ABC):
        """
        Column management class.

        - Attributes:
            - meta: Column metadata.
            - link_column: ORM column.
            - orm: ORM instance.
        """

        meta: ColumnMeta
        _link_column: Any
        orm: ORM

        @abstractmethod
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """
            Column class constructor.

            :param *args: Arguments.
            :param **kwargs: Named arguments.
            """

            pass

        @abstractmethod
        def set_name(self, name: str) -> ORM.Column | ORM.ForeignKeyColumn:
            """
            Changes the column name.

            :param name: Column name.
            :return: Column.
            """

            pass

        @staticmethod
        def _name_for_request(name: str) -> str:
            """
            Returns the column name for an SQL request.

            :param name: Column name.
            :return: Column name for SQL request.
            """
            return f'"{name}"'

        @staticmethod
        def _nullable_for_request(nullable: bool) -> str:
            """
            Returns the nullability constraint for an SQL request.

            :param nullable: Column nullability.
            :return: Nullability constraint for SQL request.
            """
            return ORM.SQL_Verbs.NOT_NULL.value if not nullable else ""

        @staticmethod
        def _default_for_request(default: Any) -> str:
            """
            Returns the default value for an SQL request.

            :return: Default value for SQL request.
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
            Returns the primary key constraint for an SQL request.

            :param primary_key: Column primary key.
            :return: Primary key constraint for SQL request.
            """
            return ORM.SQL_Verbs.PRIMARYKEY.value if primary_key else ""

        @staticmethod
        def _unique_for_request(unique: bool) -> str:
            """
            Returns the unique constraint for an SQL request.

            :param unique: Column uniqueness.
            :return: Unique constraint for SQL request.
            """
            return ORM.SQL_Verbs.UNIQUE.value if unique else ""

        @staticmethod
        def _foreign_key_for_request(
            column: ColumnMeta | ForeignKeyColumnMeta, foreign_table_name: str
        ) -> str:
            """
            Returns the foreign key constraint for an SQL request.
            :param column: Column.
            :return: Foreign key constraint for SQL request.
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
        Foreign key column management class.

        - Attributes:
            - meta: Column metadata.
            - link_column: ORM column.
            - orm: ORM instance.
        """

        meta: ForeignKeyColumnMeta

    class UniqueConstraint(ABC):
        """
        Unique constraint management class.

        - Attributes:
            - name: Constraint name.
            - columns: Columns.
            - link_constraint: ORM constraint.
        """

        name: str
        columns: set[str]
        _link_constraint: Any

    class NoSuchTableError(Exception):
        """
        Table not found error.
        """

        pass

    class CreateTableError(Exception):
        """
        Table creation error.
        """

        pass

    class SQLExecutionError(Exception):
        """
        SQL execution error.
        """

        pass

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        ORM layer constructor for SQLAlchemy.

        :param engine_url: Database connection URL.
        """

        pass

    @staticmethod
    def get_no_such_table_error() -> Type[Exception]:
        """
        Returns the table not found error.
        :return: Table not found error.
        """

        return Exception

    @abstractmethod
    def close_session(self, *args: Any, **kwargs: Any) -> None:
        """
        Closes a session.

        :param *args: Arguments.
        :param **kwargs: Named arguments.
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
        Gets or creates a table.

        :param table_name: Table name.
        :param columns: Table columns.
        :param unique_constraints_columns: Unique constraints.
        :return: Table.
        """

        pass

    @abstractmethod
    def get_tables(self) -> dict[str, Table]:
        """
        Gets all database tables.

        :return: Tables.
        """

        pass

    @abstractmethod
    def get_table(self, table_name: str) -> Table:
        """
        Gets a database table.

        :param table_name: Table name.
        :return: Table.
        """

        pass

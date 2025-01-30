"""
Database schema metadata.

- Classes:
    - ColumnMetaDict: Column metadata dictionary.
    - ColumnMeta: Column metadata.
    - ForeignKeyColumnMetaDict: Foreign key column metadata dictionary.
    - ForeignKeyColumnMeta: Foreign key column metadata.
    - ColumnType: Column types.
    - DefaultDate: Default date types.
    - ForeignKeyAction: Foreign key actions.
    - UniqueColumnsMeta: Unique columns metadata.
    - TableMetaDict: Table metadata dictionary.
    - DatabaseMetaDict: Database metadata dictionary.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, field_validator, ValidationInfo
from typing import Any, TypedDict
from re import match
from datetime import datetime, date


class ColumnType(str, Enum):
    """
    Column types.
    """

    INT = "INT"
    VARCHAR = "VARCHAR"
    TEXT = "TEXT"
    DATE = "DATE"
    DATETIME = "DATETIME"
    BOOLEAN = "BOOLEAN"
    DECIMAL = "DECIMAL"


class DefaultDate(str, Enum):
    """
    Date types.
    """

    CURRENT_DATE = "today"
    CURRENT_TIMESTAMP = "now"


class ForeignKeyAction(str, Enum):
    """
    Foreign key actions.
    """

    CASCADE = "CASCADE"
    SET_NULL = "SET NULL"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO ACTION"
    SET_DEFAULT = "SET DEFAULT"

    @staticmethod
    def create(action: str) -> ForeignKeyAction:
        """
        Creates a foreign key action.

        :param action: Foreign key action.
        :return: Foreign key action.
        """

        return {
            "": ForeignKeyAction.NO_ACTION,
            "CASCADE": ForeignKeyAction.CASCADE,
            "SET NULL": ForeignKeyAction.SET_NULL,
            "RESTRICT": ForeignKeyAction.RESTRICT,
            "NO ACTION": ForeignKeyAction.NO_ACTION,
            "SET DEFAULT": ForeignKeyAction.SET_DEFAULT,
        }[action]


class ColumnMetaDict(TypedDict):
    """
    Column metadata dictionary.

    :param name: Column name.
    :param type: Column type.
    :param length: Column length.
    :param nullable: Nullable column.
    :param primary_key: Primary key column.
    :param unique: Unique column.
    :param default: Column default value.
    """

    name: str
    type: str
    length: int | None
    nullable: bool
    primary_key: bool
    unique: bool
    default: Any | None


class ColumnMeta(BaseModel):
    """
    Column metadata.

    :param name: Column name.
    :param type: Column type.
    :param length: Column length.
    :param nullable: Nullable column.
    :param primary_key: Primary key column.
    :param unique: Unique column.
    :param default: Column default value.
    """

    name: str
    type: ColumnType
    length: int | None
    nullable: bool
    primary_key: bool
    unique: bool
    default: Any | None = None

    @field_validator("length")
    def check_length(cls, value: int | None, info: ValidationInfo) -> int | None:
        """
        Validates column length.

        :param value: Column length.
        :param info: Validation information.
        """

        if value is not None:
            if (
                info.data["type"] != ColumnType.VARCHAR
                and info.data["type"] != ColumnType.TEXT
            ):
                raise ValueError("Length is not supported for this column type.")

            if value <= 0:
                raise ValueError("Length must be positive.")

            if info.data["type"] == ColumnType.TEXT and value > 65535:
                raise ValueError("Maximum length for a TEXT field is 65535.")

            if info.data["type"] == ColumnType.VARCHAR and value > 255:
                raise ValueError("Maximum length for a VARCHAR field is 255.")

        return value

    @field_validator("default")
    def check_default(cls, value: Any, info: ValidationInfo) -> Any:
        """
        Validates column default value.

        :param value: Column default value.
        :param info: Validation information.
        :return: Column default value.
        """

        if value is not None:
            if info.data["type"] == ColumnType.BOOLEAN and not isinstance(value, bool):
                raise ValueError("Default value must be a boolean for a BOOLEAN field.")

            if info.data["type"] == ColumnType.INT and not isinstance(value, int):
                raise ValueError("Default value must be an integer for an INT field.")

            if info.data["type"] == ColumnType.DECIMAL and not isinstance(value, float):
                raise ValueError("Default value must be a float for a DECIMAL field.")

            if info.data["type"] == ColumnType.VARCHAR and not isinstance(value, str):
                raise ValueError("Default value must be a string for a VARCHAR field.")

            if info.data["type"] == ColumnType.TEXT and not isinstance(value, str):
                raise ValueError("Default value must be a string for a TEXT field.")

            if info.data["type"] == ColumnType.DATE:
                if isinstance(value, date):
                    return value
                elif isinstance(value, str):
                    if match(r"^\d{2}/\d{2}/\d{4}$", value):
                        return date.fromisoformat(
                            f"{value[6:]}-{value[3:5]}-{value[:2]}"
                        )
                    elif match(r"^\d{2}-\d{2}-\d{4}$", value):
                        return date.fromisoformat(
                            f"{value[6:]}-{value[3:5]}-{value[:2]}"
                        )
                    elif match(r"^\d{4}/\d{2}/\d{2}$", value):
                        return date.fromisoformat(
                            f"{value[:4]}-{value[5:7]}-{value[8:]}"
                        )
                    elif match(r"^\d{4}-\d{2}-\d{2}$", value):
                        return date.fromisoformat(value)
                    elif value == DefaultDate.CURRENT_DATE.value:
                        return date.today()
                    else:
                        raise ValueError(
                            "This value is not supported for a DATE field."
                        )
                else:
                    raise ValueError("This value is not supported for a DATE field.")

            if info.data["type"] == ColumnType.DATETIME:
                if isinstance(value, datetime):
                    return value
                elif isinstance(value, str):
                    if match(r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$", value):
                        return datetime.strptime(
                            f"{value[6:]}-{value[3:5]}-{value[:2]} {value[11:]}",
                            "%Y-%m-%d %H:%M:%S",
                        )
                    elif match(r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}$", value):
                        return datetime.strptime(
                            f"{value[6:]}-{value[3:5]}-{value[:2]} {value[11:]}",
                            "%Y-%m-%d %H:%M:%S",
                        )
                    elif match(r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$", value):
                        return datetime.strptime(
                            f"{value[:4]}-{value[5:7]}-{value[8:]} {value[11:]}",
                            "%Y-%m-%d %H:%M:%S",
                        )
                    elif match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", value):
                        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    elif value == DefaultDate.CURRENT_TIMESTAMP.value:
                        return datetime.now()
                    else:
                        raise ValueError(
                            "This value is not supported for a DATETIME field."
                        )
                else:
                    raise ValueError(
                        "This value is not supported for a DATETIME field."
                    )

        return value

    def get_dict(self) -> ColumnMetaDict:
        """
        Gets column metadata as a dictionary.

        :return: Column metadata dictionary.
        """

        return {
            "name": self.name,
            "type": self.type.value,
            "length": self.length,
            "nullable": self.nullable,
            "primary_key": self.primary_key,
            "unique": self.unique,
            "default": self.default,
        }


class ForeignKeyColumnMetaDict(ColumnMetaDict):
    """
    Foreign key column metadata dictionary.

    :param name: Column name.
    :param type: Column type.
    :param length: Column length.
    :param nullable: Nullable column.
    :param primary_key: Primary key column.
    :param unique: Unique column.
    :param default: Column default value.
    :param foreign_table_name: Referenced table name.
    :param foreign_column_name: Referenced column name.
    :param on_delete: Action on delete.
    :param on_update: Action on update.
    """

    foreign_table: str
    foreign_column: str
    on_delete: str
    on_update: str


class ForeignKeyColumnMeta(ColumnMeta):
    """
    Foreign key column metadata.

    :param name: Column name.
    :param type: Column type.
    :param length: Column length.
    :param nullable: Nullable column.
    :param primary_key: Primary key column.
    :param unique: Unique column.
    :param default: Column default value.
    :param foreign_table_name: Referenced table name.
    :param foreign_column_name: Referenced column name.
    :param on_delete: Action on delete.
    :param on_update: Action on update.
    """

    foreign_table_name: str
    foreign_column_name: str
    on_delete: ForeignKeyAction = ForeignKeyAction.NO_ACTION
    on_update: ForeignKeyAction = ForeignKeyAction.NO_ACTION

    def get_dict(self) -> ForeignKeyColumnMetaDict:
        """
        Gets column metadata as a dictionary.

        :return: Column metadata dictionary.
        """

        return {
            "name": self.name,
            "type": self.type.value,
            "length": self.length,
            "nullable": self.nullable,
            "primary_key": self.primary_key,
            "unique": self.unique,
            "default": self.default,
            "foreign_table": self.foreign_table_name,
            "foreign_column": self.foreign_column_name,
            "on_delete": self.on_delete.value,
            "on_update": self.on_update.value,
        }


class UniqueColumnsMeta(BaseModel):
    """
    Unique columns metadata.

    :param name: Constraint name.
    :param columns: Unique columns.
    """

    name: str
    columns: set[str]


class TableMetaDict(TypedDict):
    """
    Table metadata dictionary.

    :param name: Table name.
    :param columns: Table columns.
    :param unique_columns: Table unique columns.
    """

    name: str
    columns: dict[str, ColumnMetaDict | ForeignKeyColumnMetaDict]
    unique_columns: dict[str, set[str]]


class DatabaseMetaDict(TypedDict):
    """
    Database metadata dictionary.

    :param name: Database name.
    :param type: Database type.
    :param tables: Database tables.
    """

    name: str
    type: str
    tables: dict[str, TableMetaDict]

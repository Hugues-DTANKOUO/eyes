"""
Méta-données d'un schéma de base de données.

- Classes:
    - ColumnMetaDict: Dictionnaire des métadonnées d'une colonne.
    - ColumnMeta: Métadonnées d'une colonne.
    - ForeignKeyColumnMetaDict: Dictionnaire des métadonnées d'une colonne de clé étrangère.
    - ForeignKeyColumnMeta: Métadonnées d'une colonne de clé étrangère.
    - ColumnType: Types de colonnes.
    - DefaultDate: Types de dates par défaut.
    - ForeignKeyAction: Actions de clé étrangère.
    - UniqueColumnsMeta: Métadonnées des colonnes uniques.
    - TableMetaDict: Dictionnaire des métadonnées d'une table.
    - DatabaseMetaDict: Dictionnaire des métadonnées d'une base de données.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, field_validator, ValidationInfo
from typing import Any, TypedDict
from re import match
from datetime import datetime, date


class ColumnType(str, Enum):
    """
    Types de colonnes.
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
    Types de colonnes.
    """

    CURRENT_DATE = "today"
    CURRENT_TIMESTAMP = "now"


class ForeignKeyAction(str, Enum):
    """
    Actions de clé étrangère.
    """

    CASCADE = "CASCADE"
    SET_NULL = "SET NULL"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO ACTION"
    SET_DEFAULT = "SET DEFAULT"

    @staticmethod
    def create(action: str) -> ForeignKeyAction:
        """
        Crée une action de clé étrangère.

        :param action: Action de clé étrangère.
        :return: Action de clé étrangère.
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
    Dictionnaire des métadonnées d'une colonne.

    :param name: Nom de la colonne.
    :param type: Type de colonne.
    :param length: Longueur de la colonne.
    :param nullable: Colonne nullable.
    :param primary_key: Colonne clé primaire.
    :param unique: Colonne unique.
    :param default: Valeur par défaut de la colonne.
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
    Métadonnées d'une colonne.

    :param name: Nom de la colonne.
    :param type: Type de colonne.
    :param length: Longueur de la colonne.
    :param nullable: Colonne nullable.
    :param primary_key: Colonne clé primaire.
    :param unique: Colonne unique.
    :param default: Valeur par défaut de la colonne.
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
        Vérifie la longueur de la colonne.

        :param value: Longueur de la colonne.
        :param info: Informations de validation.
        """

        if value is not None:
            if (
                info.data["type"] != ColumnType.VARCHAR
                and info.data["type"] != ColumnType.TEXT
            ):
                raise ValueError(
                    "La longueur n'est pas supportée pour ce type de colonne."
                )

            if value <= 0:
                raise ValueError("La longueur doit être positive.")

            if info.data["type"] == ColumnType.TEXT and value > 65535:
                raise ValueError(
                    "La longueur maximale pour un champ TEXT est de 65535."
                )

            if info.data["type"] == ColumnType.VARCHAR and value > 255:
                raise ValueError(
                    "La longueur maximale pour un champ VARCHAR est de 255."
                )

        return value

    @field_validator("default")
    def check_default(cls, value: Any, info: ValidationInfo) -> Any:
        """
        Vérifie la valeur par défaut de la colonne.

        :param value: Valeur par défaut de la colonne.
        :param info: Informations de validation.
        :return: Valeur par défaut de la colonne.
        """

        if value is not None:
            if info.data["type"] == ColumnType.BOOLEAN and not isinstance(value, bool):
                raise ValueError(
                    "La valeur par défaut doit être un booléen pour un champ BOOLEAN."
                )

            if info.data["type"] == ColumnType.INT and not isinstance(value, int):
                raise ValueError(
                    "La valeur par défaut doit être un entier pour un champ INT."
                )

            if info.data["type"] == ColumnType.DECIMAL and not isinstance(value, float):
                raise ValueError(
                    "La valeur par défaut doit être un flottant pour un champ DECIMAL."
                )

            if info.data["type"] == ColumnType.VARCHAR and not isinstance(value, str):
                raise ValueError(
                    "La valeur par défaut doit être une chaîne de caractères pour un champ VARCHAR."
                )

            if info.data["type"] == ColumnType.TEXT and not isinstance(value, str):
                raise ValueError(
                    "La valeur par défaut doit être une chaîne de caractères pour un champ TEXT."
                )

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
                            "Cette valeur n'est pas supportée pour un champ DATE."
                        )
                else:
                    raise ValueError(
                        "Cette valeur n'est pas supportée pour un champ DATE."
                    )

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
                            "Cette valeur n'est pas supportée pour un champ DATETIME."
                        )
                else:
                    raise ValueError(
                        "Cette valeur n'est pas supportée pour un champ DATETIME."
                    )

        return value

    def get_dict(self) -> ColumnMetaDict:
        """
        Récupère les métadonnées de la colonne sous forme de dictionnaire.

        :return: Métadonnées de la colonne sous forme de dictionnaire.
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
    Dictionnaire des métadonnées d'une colonne de clé étrangère.

    :param name: Nom de la colonne.
    :param type: Type de colonne.
    :param length: Longueur de la colonne.
    :param nullable: Colonne nullable.
    :param primary_key: Colonne clé primaire.
    :param unique: Colonne unique.
    :param default: Valeur par défaut de la colonne.
    :param foreign_table_name: Nom de la table étrangère.
    :param foreign_column_name: Nom de la colonne étrangère.
    :param on_delete: Action en cas de suppression.
    :param on_update: Action en cas de mise à jour.
    """

    foreign_table: str
    foreign_column: str
    on_delete: str
    on_update: str


class ForeignKeyColumnMeta(ColumnMeta):
    """
    Métadonnées d'une colonne de clé étrangère.

    :param name: Nom de la colonne.
    :param type: Type de colonne.
    :param length: Longueur de la colonne.
    :param nullable: Colonne nullable.
    :param primary_key: Colonne clé primaire.
    :param unique: Colonne unique.
    :param default: Valeur par défaut de la colonne.
    :param foreign_table_name: Nom de la table étrangère.
    :param foreign_column_name: Nom de la colonne étrangère.
    :param on_delete: Action en cas de suppression.
    :param on_update: Action en cas de mise à jour.
    """

    foreign_table_name: str
    foreign_column_name: str
    on_delete: ForeignKeyAction = ForeignKeyAction.NO_ACTION
    on_update: ForeignKeyAction = ForeignKeyAction.NO_ACTION

    def get_dict(self) -> ForeignKeyColumnMetaDict:
        """
        Récupère les métadonnées de la colonne sous forme de dictionnaire.

        :return: Métadonnées de la colonne sous forme de dictionnaire.
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
    Métadonnées des colonnes uniques.

    :param name: Nom de la contrainte.
    :param columns: Colonnes uniques.
    """

    name: str
    columns: set[str]


class TableMetaDict(TypedDict):
    """
    Dictionnaire des métadonnées d'une table.

    :param name: Nom de la table.
    :param columns: Colonnes de la table.
    :param unique_columns: Colonnes uniques de la table.
    """

    name: str
    columns: dict[str, ColumnMetaDict | ForeignKeyColumnMetaDict]
    unique_columns: dict[str, set[str]]


class DatabaseMetaDict(TypedDict):
    """
    Dictionnaire des métadonnées d'une base de données.

    :param name: Nom de la base de données.
    :param type: Type de la base de données.
    :param tables: Tables de la base de données.
    """

    name: str
    type: str
    tables: dict[str, TableMetaDict]

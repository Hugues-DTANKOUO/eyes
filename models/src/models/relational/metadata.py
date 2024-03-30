"""
Méta-données d'un schéma de base de données.

- Classes:
    - ColumnMeta: Métadonnées d'une colonne.
    - ColumnType: Types de colonnes.
"""

from typing import TypedDict
from enum import Enum


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


class ColumnMeta(TypedDict):
    """
    Métadonnées d'une colonne.
    """

    name: str
    type: ColumnType
    length: int | None
    nullable: bool
    primary_key: bool
    unique: bool

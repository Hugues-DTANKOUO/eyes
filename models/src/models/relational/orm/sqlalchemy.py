from __future__ import annotations

from sqlalchemy import (
    Engine,
    create_engine,
    Table,
    MetaData,
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Float,
    ForeignKey,
    Date,
    Text,
)
from sqlalchemy.exc import NoSuchTableError as SQLAlchemyNoSuchTableError
from typing import cast, Type

from models.relational.orm import ORM
from models.relational.metadata import (
    ColumnMeta,
    ColumnType,
    ForeignKeyColumnMeta,
    ForeignKeyAction,
)
from copy import deepcopy


def get_sqlalchemy_type(column_type: ColumnType, column_length: int | None) -> type:
    """
    Retourne le type SQLAlchemy correspondant à un type de colonne.
    :param column_type: Type de colonne.
    :param column_length: Longueur de la colonne.
    :return: Type SQLAlchemy.
    """

    return {
        ColumnType.INT: cast(type, Integer),
        ColumnType.VARCHAR: (
            cast(type, String)
            if column_length is None
            else cast(type, String(column_length))
        ),
        ColumnType.TEXT: (
            cast(type, Text)
            if column_length is None
            else cast(type, Text(column_length))
        ),
        ColumnType.DATE: cast(type, Date),
        ColumnType.DATETIME: cast(type, DateTime),
        ColumnType.BOOLEAN: cast(type, Boolean),
        ColumnType.DECIMAL: cast(type, Float),
    }[column_type]


def get_column_type(column_type: type) -> ColumnType:
    """
    Retourne le type de colonne correspondant à un type SQLAlchemy.
    :param column_type: Type SQLAlchemy.
    :return: Type de colonne.
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


class SQLAlchemy(ORM):
    """
    Classe de gestion de la couche ORM pour SQLAlchemy.

    - Classes:
        - Table: Classe de gestion des tables.
        - Column: Classe de gestion des colonnes.
        - NoSuchTableError: Erreur de table inexistante.

    - Attributs:
        - engine: Moteur de connexion à la base de données.
        - no_such_table_error: Erreur de table inexistante.
        - _metadata: Métadonnées de la base de données.
    """

    engine: Engine
    _metadata: MetaData

    class Table(ORM.Table):
        """
        Classe de gestion des tables.

        - Attributs:
            - link_table: Table liée.
            - name: Nom de la table.
            - columns: Colonnes.
        """

        link_table: Table
        name: str
        columns: list[ColumnMeta | ForeignKeyColumnMeta]

        @staticmethod
        def create(table: Table) -> SQLAlchemy.Table:
            """
            Crée une table.
            :param table: Table à créer.
            :return: Table.
            """

            table_orm = cast(SQLAlchemy.Table, table)
            table_orm.link_table = deepcopy(table)
            columns: list[ColumnMeta | ForeignKeyColumnMeta] = []
            for column in table.columns:
                column_meta = ColumnMeta(
                    name=column.name,
                    type=get_column_type(cast(type, column.type)),
                    length=getattr(column.type, "length", None),
                    nullable=column.nullable or False,
                    primary_key=column.primary_key,
                    unique=column.unique or False,
                    default=column.default,
                )
                if column.foreign_keys:
                    column_meta = ForeignKeyColumnMeta(
                        name=column.name,
                        type=get_column_type(cast(type, column.type)),
                        length=getattr(column.type, "length", None),
                        nullable=column.nullable or False,
                        primary_key=column.primary_key,
                        unique=column.unique or False,
                        default=column.default,
                        foreign_table_name=next(
                            iter(column.foreign_keys)
                        ).column.table.name,
                        foreign_column_name=next(iter(column.foreign_keys)).column.name,
                        on_delete=ForeignKeyAction.create(
                            next(iter(column.foreign_keys)).ondelete or ""
                        ),
                        on_update=ForeignKeyAction.create(
                            next(iter(column.foreign_keys)).onupdate or ""
                        ),
                    )
                columns.append(column_meta)
            table_orm.columns = columns

            return table_orm

    class Column(ORM.Column):
        """
        Classe de gestion des colonnes.
        """

        link_column: Column

        @staticmethod
        def create(column: Column) -> SQLAlchemy.Column:
            """
            Crée une colonne.
            :param column: Colonne à créer.
            :return: Colonne.
            """

            column_orm = cast(SQLAlchemy.Column, column)

            column_orm.link_column = deepcopy(column)

            column_orm.name = str(column["name"])
            column_orm.type = cast(ColumnType, column["type"])
            column_orm.length = int(column["length"])
            column_orm.nullable = bool(column["nullable"])
            column_orm.primary_key = bool(column["primary_key"])
            column_orm.unique = bool(column["unique"])
            column_orm.default = column["default"]

            return column_orm

    class ForeignKeyColumn(ORM.ForeignKeyColumn):
        """
        Classe de gestion des colonnes de clé étrangère.
        """

        link_column: Column

        @staticmethod
        def create(column: Column) -> SQLAlchemy.ForeignKeyColumn:
            """
            Crée une colonne.
            :param column: Colonne à créer.
            :return: Colonne.
            """

            column_orm = cast(
                SQLAlchemy.ForeignKeyColumn, SQLAlchemy.Column.create(column)
            )

            foreign_key = next(iter(column_orm.link_column.foreign_keys))

            column_orm.foreign_table_name = foreign_key.column.table.name
            column_orm.foreign_column_name = foreign_key.column.name
            column_orm.on_delete = ForeignKeyAction.create(foreign_key.ondelete or "")
            column_orm.on_update = ForeignKeyAction.create(foreign_key.onupdate or "")

            return column_orm

    class NoSuchTableError(SQLAlchemyNoSuchTableError):
        """
        Erreur de table inexistante.
        """

        pass

    def __init__(self, engine_url: str) -> None:
        """
        Constructeur de la couche ORM pour SQLAlchemy.
        :param engine_url: URL de connexion à la base de données.
        """

        self.engine = create_engine(engine_url)
        self._metadata = MetaData()
        self._metadata.reflect(bind=self.engine)

    def get_or_create_table(
        self,
        table_name: str,
        columns: list[ColumnMeta | ForeignKeyColumnMeta] | None = None,
        ensure_exists: bool = False,
    ) -> SQLAlchemy.Table:
        """
        Récupère ou crée une table.
        :param table_name: Nom de la table.
        :param columns: Colonnes de la table.
        :param ensure_exists: Assure l'existence de la table.
        :return: Table.
        """
        try:
            return self.Table.create(
                Table(table_name, self._metadata, autoload_with=self.engine)
            )
        except SQLAlchemyNoSuchTableError:
            if ensure_exists:
                if not columns:
                    raise self.CreateTableError(
                        f"Impossible de créer la table {table_name}.\n"
                        "Aucune colonne n'a été spécifiée."
                    )
                try:
                    has_primary_key = False
                    for column in columns:
                        if column.primary_key:
                            has_primary_key = True
                            break
                    if not has_primary_key:
                        raise self.CreateTableError(
                            f"Impossible de créer la table {table_name}.\n"
                            "Aucune colonne primaire n'a été spécifiée."
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
                                    default=column.default,
                                )
                                if isinstance(column, ForeignKeyColumnMeta)
                                else Column(
                                    column.name,
                                    get_sqlalchemy_type(column.type, column.length),
                                    nullable=column.nullable,
                                    primary_key=column.primary_key,
                                    unique=column.unique,
                                    default=column.default,
                                )
                            )
                            for column in columns
                        ],
                        extend_existing=True,
                    )
                    table.create(bind=self.engine, checkfirst=True)
                    return self.Table.create(table)
                except Exception as e:
                    raise self.CreateTableError(
                        f"Impossible de créer la table {table_name}."
                    ) from e
            else:
                raise self.NoSuchTableError(f"La table {table_name} n'existe pas.")

    @staticmethod
    def get_no_such_table_error() -> Type[SQLAlchemyNoSuchTableError]:
        """
        Retourne l'erreur de table inexistante.
        :return: Erreur de table inexistante.
        """

        return SQLAlchemyNoSuchTableError

    def close_session(self) -> None:
        """Ferme la connexion à la base de données."""
        self.engine.dispose()

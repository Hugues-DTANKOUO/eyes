from __future__ import annotations

from sqlalchemy import (
    Engine,
    create_engine,
    Connection,
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
    UniqueConstraint,
    TextClause,
)
from sqlalchemy.exc import (
    NoSuchTableError as SQLAlchemyNoSuchTableError,
    SQLAlchemyError,
)
from sqlalchemy.sql.schema import DefaultClause
from sqlalchemy.sql import text
from typing import cast, Type, Any

from models.relational.orm import ORM
from models.relational.metadata import (
    ColumnMeta,
    ColumnType,
    ForeignKeyColumnMeta,
    ForeignKeyAction,
    UniqueColumnsMeta,
)
from copy import copy

SQLALCHEMY_TYPES: dict[ColumnType, type] = {
    ColumnType.INT: cast(type, Integer),
    ColumnType.VARCHAR: cast(type, String),
    ColumnType.TEXT: cast(type, Text),
    ColumnType.DATE: cast(type, Date),
    ColumnType.DATETIME: cast(type, DateTime),
    ColumnType.BOOLEAN: cast(type, Boolean),
    ColumnType.DECIMAL: cast(type, Float),
}


def get_sqlalchemy_type(column_type: ColumnType, column_length: int | None) -> type:
    """
    Retourne le type SQLAlchemy correspondant à un type de colonne.
    :param column_type: Type de colonne.
    :param column_length: Longueur de la colonne.
    :return: Type SQLAlchemy.
    """

    type_alchemy = SQLALCHEMY_TYPES[column_type]
    if column_length is not None and (type_alchemy == String or type_alchemy == Text):
        type_alchemy = cast(type, String(length=column_length))
    return type_alchemy


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


def cast_default(default: Any | None, column_type: type) -> Any:
    """
    Convertit la valeur par défaut d'une colonne.
    :param default: Valeur par défaut.
    :param column_type: Type de la colonne.
    :return: Valeur par défaut.
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
    schema: str | None
    _metadata: MetaData

    class Table(ORM.Table):
        """
        Classe de gestion des tables.

        - Attributs:
            - link_table: Table liée.
            - name: Nom de la table.
            - columns_meta: Métadonnées des colonnes.
        """

        link_table: Table
        _name: str
        columns: list[SQLAlchemy.Column | SQLAlchemy.ForeignKeyColumn]
        unique_constraints: list[UniqueColumnsMeta]
        orm: SQLAlchemy

        def __init__(self, table: Table, sql_alchemy_instance: SQLAlchemy) -> None:
            """
            Crée une table.
            :param table: Table à créer.
            :param sql_alchemy_instance: Instance de la couche ORM pour SQLAlchemy.
            :return: Table.
            """

            self._name = table.name
            self.link_table = copy(table)
            self.columns = []
            for column in table.columns:
                if column.foreign_keys:
                    column_orm: SQLAlchemy.Column | SQLAlchemy.ForeignKeyColumn = (
                        SQLAlchemy.ForeignKeyColumn(column, sql_alchemy_instance)
                    )
                else:
                    column_orm = SQLAlchemy.Column(column, sql_alchemy_instance)
                self.columns.append(column_orm)
            self.unique_constraints = []
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
            self.orm = sql_alchemy_instance

        def add_column(
            self,
            column: ColumnMeta | ForeignKeyColumnMeta,
        ) -> SQLAlchemy.Column | SQLAlchemy.ForeignKeyColumn:
            """
            Ajoute une colonne à la table.
            :param column: Colonne à créer.
            :return: Colonne.
            """

            if column.name in self.link_table.columns:
                raise self.AddColumnError(
                    f"Impossible de créer la colonne {column.name}.\n"
                    f"La colonne existe déjà dans la table {self.name}."
                )

            with self.orm.engine.connect() as connection:
                try:
                    name = (
                        f'{self.orm.schema}."{self.name}"'
                        if self.orm.schema
                        else self.name
                    )
                    column_type = cast(
                        Integer | String | DateTime | Boolean | Float | Date | Text,
                        get_sqlalchemy_type(column.type, column.length),
                    )
                    column_type_compiled = column_type.compile(self.orm.engine.dialect)
                    nullable = "NOT NULL" if not column.nullable else ""
                    default = ""
                    if column.default is not None:
                        if isinstance(column.default, str):
                            default = f"DEFAULT '{column.default}'"
                        else:
                            default = f"DEFAULT {column.default}"
                    primary_key = "PRIMARY KEY" if column.primary_key else ""
                    unique = "UNIQUE" if column.unique else ""
                    foreign_key = ""
                    if isinstance(column, ForeignKeyColumnMeta):
                        foreign_table_name = (
                            f'{self.orm.schema}."{column.foreign_table_name}"'
                            if self.orm.schema
                            else column.foreign_table_name
                        )
                        foreign_key = (
                            f'FOREIGN KEY ("{column.name}") REFERENCES {foreign_table_name} ("{column.foreign_column_name}")'
                            f" ON DELETE {column.on_delete.value}"
                            f" ON UPDATE {column.on_update.value}"
                        )
                    alter_statement = text(
                        f'ALTER TABLE {name} ADD COLUMN "{column.name}" {column_type_compiled}'
                        f" {nullable} {default} {primary_key} {unique} {foreign_key}"
                    )
                    self.orm.execute(connection, alter_statement)
                    self = self.orm.get_table(self.name)
                    return self.get_column(column.name)
                except Exception as e:
                    raise self.AddColumnError(
                        f"Impossible de créer la colonne {column.name} dans la table {self.name}."
                    ) from e

        def get_column(
            self, name: str
        ) -> SQLAlchemy.Column | SQLAlchemy.ForeignKeyColumn:
            """
            Récupère une colonne de la table.
            :param name: Nom de la colonne.
            :return: Colonne.
            """
            try:
                column = self.link_table.columns[name]
                if column.foreign_keys:
                    return SQLAlchemy.ForeignKeyColumn(column, self.orm)
                return SQLAlchemy.Column(self.link_table.columns[name], self.orm)
            except KeyError as e:
                raise KeyError(
                    f"La colonne {name} n'existe pas dans la table {self.name}."
                ) from e

        @property
        def name(self) -> str:
            """
            Retourne le nom de la table.
            :return: Nom de la table.
            """

            return self._name

        @name.setter
        def name(self, name: str) -> None:
            """
            Modifie le nom de la table.
            :param name: Nom de la table.
            """
            try:
                with self.orm.engine.connect() as connection:
                    alter_statement = text(
                        f'ALTER TABLE {self.orm.schema}."{self._name}" RENAME TO "{name}"'
                    )
                    self.orm.execute(connection, alter_statement)
                    self = self.orm.get_table(name)
            except SQLAlchemyError as e:
                raise self.orm.SQLExecutionError(
                    f"Impossible de renommer la table {self._name} en {name}."
                ) from e

    class Column(ORM.Column):
        """
        Classe de gestion des colonnes.
        """

        meta: ColumnMeta
        link_column: Column
        orm: SQLAlchemy

        def __init__(self, column: Column, sql_alchemy_instance: SQLAlchemy) -> None:
            """
            Crée une colonne.
            :param column: Colonne à créer.
            :param sql_alchemy_instance: Instance de la couche ORM pour SQLAlchemy.
            :return: Colonne.
            """

            self.link_column = copy(column)

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
            self.orm = sql_alchemy_instance

        def set_name(self, name: str) -> SQLAlchemy.Column:
            """
            Modifie le nom de la colonne.
            :param name: Nom de la colonne.
            :return: Colonne.
            """
            try:
                with self.orm.engine.connect() as connection:
                    alter_statement = text(
                        f'ALTER TABLE {self.orm.schema}."{self.link_column.table.name}"'
                        f' RENAME COLUMN "{self.meta.name}" TO "{name}"'
                    )
                    self.orm.execute(connection, alter_statement)
                    table = self.orm.get_table(self.link_column.table.name)
                    self = cast(SQLAlchemy.Column, table.get_column(name))
                    return self
            except SQLAlchemyError as e:
                raise self.orm.SQLExecutionError(
                    f"Impossible de renommer la colonne {self.link_column.name} en {name}."
                ) from e

    class ForeignKeyColumn(ORM.ForeignKeyColumn):
        """
        Classe de gestion des colonnes de clé étrangère.
        """

        link_column: Column
        orm: SQLAlchemy

        def __init__(self, column: Column, sql_alchemy_instance: SQLAlchemy) -> None:
            """
            Crée une colonne.
            :param column: Colonne à créer.
            :param sql_alchemy_instance: Instance de la couche ORM pour SQLAlchemy.
            :return: Colonne.
            """

            foreign_key = next(iter(column.foreign_keys))

            self.link_column = copy(column)

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
            self.orm = sql_alchemy_instance

        def set_name(self, name: str) -> SQLAlchemy.ForeignKeyColumn:
            """
            Modifie le nom de la colonne.
            :param name: Nom de la colonne.
            :return: Colonne.
            """
            return cast(SQLAlchemy.ForeignKeyColumn, super().set_name(name))  # type: ignore

    class UniqueConstraint(ORM.UniqueConstraint):
        """
        Classe de gestion des contraintes d'unicité.
        """

        link_constraint: UniqueConstraint

        @staticmethod
        def create(constraint: UniqueConstraint) -> SQLAlchemy.UniqueConstraint:
            """
            Crée une contrainte d'unicité.
            :param constraint: Contrainte d'unicité à créer.
            :return: Contrainte d'unicité.
            """

            constraint_orm = cast(SQLAlchemy.UniqueConstraint, constraint)

            constraint_orm.link_constraint = copy(constraint)
            constraint_orm.name = str(constraint.name or "")
            constraint_orm.columns = set(column.name for column in constraint.columns)

            return constraint_orm

    class NoSuchTableError(SQLAlchemyNoSuchTableError):
        """
        Erreur de table inexistante.
        """

        pass

    def __init__(self, engine_url: str, schema: str) -> None:
        """
        Constructeur de la couche ORM pour SQLAlchemy.
        :param engine_url: URL de connexion à la base de données.
        :param schema: Schéma/partition de la base de données.
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
        Récupère ou crée une table.
        :param table_name: Nom de la table.
        :param columns: Colonnes de la table.
        :param unique_constraints_columns: Contraintes d'unicité.
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
            raise self.CreateTableError(
                f"Impossible de créer la table {table_name}."
            ) from e

    def get_tables(self) -> dict[str, ORM.Table]:
        """
        Récupère les tables de la base de données.
        :return: Tables.
        """

        return {
            table_name: self.Table(table, self)
            for table_name, table in self._metadata.tables.items()
        }

    def get_table(self, table_name: str) -> SQLAlchemy.Table:
        """
        Récupère une table de la base de données.
        :param table_name: Nom de la table.
        :return: Table.
        """
        table_name = f"{self.schema}.{table_name}" if self.schema else table_name
        if table_name not in self._metadata.tables:
            raise self.NoSuchTableError(f"La table {table_name} n'existe pas.")
        return self.Table(self._metadata.tables[table_name], self)

    @staticmethod
    def get_no_such_table_error() -> Type[SQLAlchemyNoSuchTableError]:
        """
        Retourne l'erreur de table inexistante.
        :return: Erreur de table inexistante.
        """

        return SQLAlchemyNoSuchTableError

    def refresh_metadata(self) -> None:
        """
        Rafraîchit les métadonnées de la base de données.
        """
        self._metadata = MetaData(schema=self.schema)
        self._metadata.reflect(bind=self.engine)

    def execute(self, connection: Connection, statement: TextClause) -> None:
        """
        Exécute une requête SQL.
        :param connection: Connexion à la base de données.
        :param statement: Requête SQL.
        """
        connection.execute(statement)
        connection.commit()
        self.refresh_metadata()

    def close_session(self) -> None:
        """Ferme la connexion à la base de données."""
        self.engine.dispose()

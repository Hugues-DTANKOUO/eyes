"""
Database configuration elements.

- Classes:
    - DbConfig: Database configuration.
    - DataBaseType: Database types.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field, field_validator


class DbConfig(BaseModel):
    """
    Database configuration elements.

    :param host: Database server address.
    :param port: Database server port.
    :param type: Database type.
    :param user: Database username.
    :param password: Database password.
    :param database: Database name.
    :param schema: Database schema/partition.
    """

    host: str = Field("localhost", title="Database server address")
    port: int = Field(..., title="Database server port")
    type: DataBaseType = Field(..., title="Database type")
    user: str = Field("root", title="Database username")
    password: str = Field(..., title="Database password")
    database: str = Field("test", title="Database name")
    db_schema: str | None = Field(None, title="Database schema/partition")

    def __init__(
        self,
        host: str,
        user: str,
        type: DataBaseType,
        password: str,
        database: str,
        port: int | None = None,
        db_schema: str | None = None,
    ) -> None:
        """
        Database configuration constructor.

        :param host: Database server address.
        :param user: Database username.
        :param type: Database type.
        :param password: Database password.
        :param database: Database name.
        :param port: Database server port.
        """

        if port is None:
            port = type.default_port()

        if db_schema is None:
            db_schema = type.default_schema()

        super().__init__(
            host=host,
            port=port,
            type=type,
            user=user,
            password=password,
            database=database,
            db_schema=db_schema,
        )

    def __str__(self) -> str:
        """Returns a string representation of the database configuration."""
        return f"DbConfig({self.host}, {self.port}, {self.user}, {self.database})"

    def __repr__(self) -> str:
        """Returns a string representation of the database configuration."""
        return f"DbConfig({self.host}, {self.port}, {self.user}, {self.database})"

    # Port validator
    @field_validator("port")
    def port_must_be_valid(cls, value: int) -> int:
        """
        Verifies that the port is a valid positive integer.

        :param value: Database server port.
        :return: Database server port.
        """
        if not (isinstance(value, int) or 1 <= abs(value) <= 65535):
            raise ValueError("Port must be a positive integer between 1 and 65535.")
        return abs(value)

    def get_engine_url(self) -> str:
        """
        Returns the database connection URL.

        :return: Database connection URL.
        """

        parameters_url = (
            f"{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        )

        return {
            DataBaseType.MYSQL: f"mysql+mysqlconnector://{parameters_url}",
            DataBaseType.POSTGRESQL: f"postgresql+psycopg2://{parameters_url}",
            DataBaseType.SQLITE: f"sqlite:///{self.database}.db",
            DataBaseType.ORACLE: f"oracle+cx_oracle://{parameters_url}",
            DataBaseType.SQLSERVER: f"mssql+pyodbc://{parameters_url}",
        }[self.type]


class DataBaseType(Enum):
    """Database types."""

    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    ORACLE = "oracle"
    SQLSERVER = "sqlserver"

    def __str__(self) -> str:
        """Returns a string representation of the database type."""
        return self.value

    def default_port(self) -> int:
        """Returns the default port for the database type."""

        return {
            DataBaseType.MYSQL: 3306,
            DataBaseType.POSTGRESQL: 5432,
            DataBaseType.SQLITE: 0,
            DataBaseType.ORACLE: 1521,
            DataBaseType.SQLSERVER: 1433,
        }[self]

    def default_schema(self) -> str:
        """Returns the default schema for the database type."""

        return {
            DataBaseType.MYSQL: "mysql",
            DataBaseType.POSTGRESQL: "public",
            DataBaseType.SQLITE: "",
            DataBaseType.ORACLE: "sys",
            DataBaseType.SQLSERVER: "dbo",
        }[self]

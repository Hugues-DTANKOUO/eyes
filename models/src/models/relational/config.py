"""
Éléments de configuration d'une base de données.

- Classes:
    - DbConfig: Configuration d'une base de données.
    - DataBaseType: Types de base de données.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field, field_validator


class DbConfig(BaseModel):
    """
    Eléments de configuration d'une base de données.

    :param host: Adresse du serveur de base de données.
    :param port: Port du serveur de base de données.
    :param type: Type de base de données.
    :param user: Nom d'utilisateur de la base de données.
    :param password: Mot de passe de la base de données.
    :param database: Nom de la base de données.
    """

    host: str = Field("localhost", title="Adresse du serveur de base de données")
    port: int = Field(..., title="Port du serveur de base de données")
    type: DataBaseType = Field(..., title="Type de base de données")
    user: str = Field("root", title="Nom d'utilisateur de la base de données")
    password: str = Field(..., title="Mot de passe de la base de données")
    database: str = Field("test", title="Nom de la base de données")

    def __init__(
        self,
        host: str,
        user: str,
        type: DataBaseType,
        password: str,
        database: str,
        port: int | None = None,
    ) -> None:
        """
        Constructeur de la configuration de la base de données.

        :param host: Adresse du serveur de base de données.
        :param user: Nom d'utilisateur de la base de données.
        :param type: Type de base de données.
        :param password: Mot de passe de la base de données.
        :param database: Nom de la base de données.
        :param port: Port du serveur de base de données.
        """

        if port is None:
            port = type.default_port()

        super().__init__(
            host=host,
            port=port,
            type=type,
            user=user,
            password=password,
            database=database,
        )

    def __str__(self) -> str:
        """Retourne une représentation de la configuration de la base de données."""
        return f"DbConfig({self.host}, {self.port}, {self.user}, {self.database})"

    def __repr__(self) -> str:
        """Retourne une représentation de la configuration de la base de données."""
        return f"DbConfig({self.host}, {self.port}, {self.user}, {self.database})"

    # Validateur pour le port
    @field_validator("port")
    def port_must_be_valid(cls, value: int) -> int:
        """
        Vérifie que le port est un entier positif.

        :param value: Port du serveur de base de données.
        :return: Port du serveur de base de données.
        """
        if not (isinstance(value, int) or 1 <= abs(value) <= 65535):
            raise ValueError(
                "Le port doit être un entier positif compris entre 1 et 65535."
            )
        return abs(value)

    def get_engine_url(self) -> str:
        """
        Retourne l'URL de connexion à la base de données.

        :return: URL de connexion à la base de données.
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
    """Types de base de données."""

    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    ORACLE = "oracle"
    SQLSERVER = "sqlserver"

    def __str__(self) -> str:
        """Retourne une représentation du type de base de données."""
        return self.value

    def default_port(self) -> int:
        """Retourne le port par défaut du type de base de données."""

        return {
            DataBaseType.MYSQL: 3306,
            DataBaseType.POSTGRESQL: 5432,
            DataBaseType.SQLITE: 0,
            DataBaseType.ORACLE: 1521,
            DataBaseType.SQLSERVER: 1433,
        }[self]

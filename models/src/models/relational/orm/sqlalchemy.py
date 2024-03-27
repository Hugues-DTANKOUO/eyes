from __future__ import annotations

from sqlalchemy import Engine, create_engine, Table, MetaData
from sqlalchemy.ext.automap import automap_base, AutomapBase
from sqlalchemy.orm import sessionmaker, Session
from typing import cast

from models.relational.orm import ORM


class SQLAlchemy(ORM):
    """
    Classe de gestion de la couche ORM pour SQLAlchemy.
    """

    engine: Engine
    _base: AutomapBase
    _metadata: MetaData
    _session: sessionmaker[Session]

    class Table(ORM.Table):
        """
        Classe de gestion des tables.
        """

        @staticmethod
        def create(table: Table) -> SQLAlchemy.Table:
            """
            Crée une table.
            :param table: Table à créer.
            """

            return cast(SQLAlchemy.Table, table)

    def __init__(self, engine_url: str) -> None:
        """
        Constructeur de la couche ORM pour SQLAlchemy.
        :param engine_url: URL de connexion à la base de données.
        """

        self.engine = create_engine(engine_url)
        self._base = cast(AutomapBase, automap_base())
        self._base.prepare(self.engine, reflect=True)
        self._metadata = MetaData()
        self._metadata.reflect(bind=self.engine)
        self._session = sessionmaker(bind=self.engine)

    def get_table(self, table_name: str) -> SQLAlchemy.Table:
        """
        Retourne une table.
        :param table_name: Nom de la table.
        :return: Table.
        """

        return self.Table.create(cast(Table, self._base.classes[table_name]))

    def get_session(self) -> Session:
        """
        Retourne une session.
        :return: Session.
        """

        return self._session()

    def close_session(self, session: Session) -> None:
        """
        Ferme une session.
        :param session: Session à fermer.
        """

        session.close()

    def close(self) -> None:
        """Ferme la connexion à la base de données."""
        self.engine.dispose()

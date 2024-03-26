from models.relational import DbConfig, DataBaseType


def test_db_config() -> None:
    """
    ÉTANT DONNÉ une configuration de base de données,
    QUAND la configuration est initialisée,
    ALORS les attributs sont correctement initialisés.
    """

    # Configuration de la base de données
    db_config = DbConfig(
        host="localhost",
        type=DataBaseType.POSTGRESQL,
        database="test",
        user="test",
        password="test",
    )

    # Attributs
    assert db_config.host == "localhost"
    assert db_config.type == DataBaseType.POSTGRESQL
    assert db_config.database == "test"
    assert db_config.user == "test"
    assert db_config.password == "test"
    assert db_config.port == 5432

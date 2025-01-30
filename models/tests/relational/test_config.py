from models.relational.db_schema import DbConfig, DataBaseType


def test_db_config() -> None:
    """
    GIVEN a database configuration,
    WHEN the configuration is initialized,
    THEN the attributes are correctly set.
    """

    # Database configuration
    db_config = DbConfig(
        host="localhost",
        type=DataBaseType.POSTGRESQL,
        database="test",
        user="test",
        password="test",
    )

    # Attributes
    assert db_config.host == "localhost"
    assert db_config.type == DataBaseType.POSTGRESQL
    assert db_config.database == "test"
    assert db_config.user == "test"
    assert db_config.password == "test"
    assert db_config.port == 5432

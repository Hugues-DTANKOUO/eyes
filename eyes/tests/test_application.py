import os
from eyes.application import (
    Module,
    APPLICATION_NAME,
    PROJECT_DIR,
    ApplicationModuleError,
    INVALID_CALL_ERROR,
    EYES,
    MODELS,
)


def test_globals_variables() -> None:
    """
    GIVEN the eyes project
    WHEN the project is initialized
    THEN global variables are correctly initialized
    """

    # Global variables
    assert APPLICATION_NAME == "Eyes"
    assert PROJECT_DIR == os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    # Modules
    assert EYES.name == "Eyes"
    assert EYES.path == os.path.join(PROJECT_DIR, "eyes")

    assert MODELS.name == "Models"
    assert MODELS.path == os.path.join(PROJECT_DIR, "models")


def test_invalid_module_creation() -> None:
    """
    GIVEN a module from the eyes project
    WHEN trying to create another module using a property of the first one
    THEN an error is raised
    """

    # Attempt to create multiple modules
    module = Module().eyes
    try:
        module.models
    except ApplicationModuleError as error:
        assert str(error) == INVALID_CALL_ERROR
    else:
        assert False

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
    ÉTANT DONNÉ le projet eyes.
    QUAND le projet est initialisé
    ALORS les variables globales sont correctement initialisées.
    """

    # Variables globales
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
    ÉTANT DONNÉ un module du projet eyes.
    QUAND on essaye de créer un autre module avec une propriété de ce dernier
    ALORS une erreur est levée.
    """

    # Tentative de création multiple d'un module
    module = Module().eyes
    try:
        module.models
    except ApplicationModuleError as error:
        assert str(error) == INVALID_CALL_ERROR
    else:
        assert False

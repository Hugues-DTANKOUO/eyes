""" Static code analysis and unit tests execution across all project modules. """

from eyes.scripts import run_lint, run_tests


def run() -> None:
    """Execute static code analysis and unit tests across all project modules."""
    run_lint.run()
    run_tests.run()

"""DriftAdapt Import Unit Tests.

Author: DriftAdapt Contributors
Purpose: Verifies that all modules within the app package structure are correctly importable.
Future Integration: Executed as part of the test suite in CI.
"""


def test_package_imports() -> None:
    """Verifies that all subpackages are importable and contain standard metadata."""
    import app
    import app.api
    import app.continual
    import app.core
    import app.datasets
    import app.drift
    import app.evaluation
    import app.experiments
    import app.federation
    import app.metrics
    import app.models
    import app.replay
    import app.services
    import app.utils
    import app.visualization

    assert app.__version__ == "0.1.0"
    assert app.__doc__ is not None
    assert app.api.__doc__ is not None
    assert app.core.__doc__ is not None
    assert app.models.__doc__ is not None
    assert app.services.__doc__ is not None
    assert app.federation.__doc__ is not None
    assert app.continual.__doc__ is not None
    assert app.drift.__doc__ is not None
    assert app.replay.__doc__ is not None
    assert app.datasets.__doc__ is not None
    assert app.evaluation.__doc__ is not None
    assert app.visualization.__doc__ is not None
    assert app.experiments.__doc__ is not None
    assert app.metrics.__doc__ is not None
    assert app.utils.__doc__ is not None

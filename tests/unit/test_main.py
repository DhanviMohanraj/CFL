"""DriftAdapt Main Entry Point Unit Tests.

Author: DriftAdapt Contributors
Purpose: Verifies the primary entrypoint function executes successfully.
Future Integration: Executed as part of the test suite in CI.
"""

from main import main


def test_main_execution() -> None:
    """Verifies that the main entrypoint returns success (0 status code)."""
    status_code = main()
    assert status_code == 0

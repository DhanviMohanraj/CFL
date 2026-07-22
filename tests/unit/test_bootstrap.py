"""DriftAdapt Bootstrap Unit Tests.

Author: DriftAdapt Contributors
Purpose: Verifies the bootstrap script behaves idempotently and creates all required directories.
Future Integration: Executed as part of the test suite in CI.
"""

from pathlib import Path

from scripts.bootstrap import REQUIRED_DIRECTORIES, bootstrap_project


def test_bootstrap_directories_created() -> None:
    """Verifies that all directories defined in REQUIRED_DIRECTORIES exist after running bootstrap."""
    # Repository root is two levels up from 'tests/unit'
    root_dir = Path(__file__).resolve().parent.parent.parent

    # Execute bootstrap
    exit_code = bootstrap_project()
    assert exit_code == 0

    # Assert all directories exist and contain a .gitkeep file
    for dir_path_str in REQUIRED_DIRECTORIES:
        target_dir = root_dir / dir_path_str
        assert target_dir.exists(), f"Directory {dir_path_str} was not created"
        gitkeep_file = target_dir / ".gitkeep"
        assert gitkeep_file.exists(), f".gitkeep missing in {dir_path_str}"


def test_bootstrap_idempotency() -> None:
    """Verifies that running bootstrap_project multiple times is idempotent and safe."""
    exit_code_1 = bootstrap_project()
    exit_code_2 = bootstrap_project()

    assert exit_code_1 == 0
    assert exit_code_2 == 0

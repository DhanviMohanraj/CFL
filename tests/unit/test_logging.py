"""DriftAdapt Logging Unit Tests.

Author: DriftAdapt Contributors
Purpose: Verifies the centralized logger formats, rotation sinks, and LoggerFactory caching.
Future Integration: Executed as part of the test suite in CI.
"""

import time
from pathlib import Path

from app.core.config import ConfigManager
from app.core.logging import LoggerFactory


def test_logger_factory_caching() -> None:
    """Verifies that LoggerFactory caches logger instances and avoids duplicates."""
    log1 = LoggerFactory.get_logger("TestModule")
    log2 = LoggerFactory.get_logger("TestModule")
    log3 = LoggerFactory.get_logger("OtherModule")

    # Identical bound contexts share the same cache instance
    assert log1 is log2
    assert log1 is not log3


def test_logger_creation_and_logs_directory() -> None:
    """Verifies that LoggerFactory creates application, errors, and startup files in logs/."""
    config = ConfigManager().get_config()
    logs_dir = Path(config.system.logs_dir)

    # Initialize Factory
    LoggerFactory.initialize()

    # Log messages to check handlers
    test_logger = LoggerFactory.get_logger("TestClient")
    test_logger.info("Normal application info log.")
    test_logger.error("Simulated application error log.")

    # Tag startup context to target startup.log
    startup_logger = LoggerFactory.get_logger("StartupCheck")
    startup_logger.bind(startup=True).info("Booting client checks.")

    # Wait for loguru async enqueue writes to flush to disk
    time.sleep(0.5)

    assert (logs_dir / "application.log").exists()
    assert (logs_dir / "errors.log").exists()
    assert (logs_dir / "startup.log").exists()

    # Read and verify content
    with open(logs_dir / "application.log", "r", encoding="utf-8") as f:
        content = f.read()
        assert "Normal application info log." in content
        assert "Simulated application error log." in content
        assert "[TestClient]" in content

    with open(logs_dir / "errors.log", "r", encoding="utf-8") as f:
        err_content = f.read()
        assert "Simulated application error log." in err_content
        assert "Normal application info log." not in err_content

    with open(logs_dir / "startup.log", "r", encoding="utf-8") as f:
        startup_content = f.read()
        assert "Booting client checks." in startup_content
        assert "Normal application info log." not in startup_content

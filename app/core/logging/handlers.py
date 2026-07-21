"""DriftAdapt Logging Handlers Configuration.

Author: DriftAdapt Contributors
Purpose: Configures console and rotating file output sinks for loguru.
Future Integration: Invoked byLoggerFactory during initialization step.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger

from app.core.logging.formatter import log_formatter


def clear_existing_handlers() -> None:
    """Removes all previously registered sinks from loguru global registry."""
    logger.remove()


def configure_logging_handlers(
    logs_dir: Path,
    log_level: str,
    console_logging: bool,
    file_logging: bool,
    rotation: str,
    retention: str,
) -> List[int]:
    """Sets up console and split rotating log files based on configuration.

    Registers:
    - stdout console log
    - application.log: general runtime records
    - errors.log: error-only logs
    - startup.log: filtered records marked with 'startup=True' extra context
    - metrics.log: filtered records marked with 'metrics_log=True' extra context

    Returns:
        List of loguru handler IDs.
    """
    # Clean previous handlers first
    clear_existing_handlers()
    handler_ids = []

    # 1. Console Log
    if console_logging:
        console_id = logger.add(
            sys.stdout,
            format=log_formatter,
            level=log_level,
            backtrace=True,
            diagnose=True,
        )
        handler_ids.append(console_id)

    # 2. File Logs
    if file_logging:
        logs_dir.mkdir(parents=True, exist_ok=True)

        # application.log (all logs matching log_level)
        app_log_id = logger.add(
            logs_dir / "application.log",
            rotation=rotation,
            retention=retention,
            format=log_formatter,
            level=log_level,
            enqueue=True,  # Thread-safe async write
            backtrace=True,
            diagnose=True,
        )
        handler_ids.append(app_log_id)

        # errors.log (ERROR and above only)
        error_log_id = logger.add(
            logs_dir / "errors.log",
            rotation=rotation,
            retention=retention,
            format=log_formatter,
            level="ERROR",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )
        handler_ids.append(error_log_id)

        # startup.log (logs tagged with extra['startup'] == True)
        startup_log_id = logger.add(
            logs_dir / "startup.log",
            rotation=rotation,
            retention=retention,
            format=log_formatter,
            level=log_level,
            filter=lambda record: record["extra"].get("startup") is True,
            enqueue=True,
        )
        handler_ids.append(startup_log_id)

        # metrics.log (logs tagged with extra['metrics_log'] == True)
        metrics_log_id = logger.add(
            logs_dir / "metrics.log",
            rotation=rotation,
            retention=retention,
            format=log_formatter,
            level=log_level,
            filter=lambda record: record["extra"].get("metrics_log") is True,
            enqueue=True,
        )
        handler_ids.append(metrics_log_id)

    return handler_ids

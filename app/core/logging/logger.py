"""DriftAdapt Logger Service Utilities.

Author: DriftAdapt Contributors
Purpose: Intercepts standard Python logging library statements and system level exceptions.
Future Integration: Provides cross-library redirection for third-party libraries (e.g. transformers).
"""

import logging
import sys
from typing import Any, Type

from loguru import logger


class InterceptHandler(logging.Handler):
    """Handler to redirect standard library logging events to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where the logged message originated
        frame: Any = sys._getframe(6)
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back

        logger.opt(depth=6, exception=record.exc_info).log(
            level, record.getMessage()
        )


def redirect_standard_logging() -> None:
    """Redirects Python standard library logging to loguru sinks."""
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Intercept loggers of external dependencies to prevent clutter
    for logger_name in ("transformers", "urllib3", "peft", "torch"):
        deps_logger = logging.getLogger(logger_name)
        deps_logger.handlers = [InterceptHandler()]
        deps_logger.propagate = False


def sys_exception_handler(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_traceback: Any,
) -> None:
    """Callback hook to log unhandled top-level exceptions via loguru."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.bind(module_name="System").opt(
        exception=(exc_type, exc_value, exc_traceback)
    ).critical(f"Unhandled system exception: {exc_value}")



def register_system_exception_hook() -> None:
    """Registers global traceback handler to intercept uncaught exceptions."""
    sys.excepthook = sys_exception_handler

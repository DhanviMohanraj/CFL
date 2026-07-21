"""DriftAdapt LoggerFactory Module.

Author: DriftAdapt Contributors
Purpose: Exposes cached, module-scoped loggers with lazy-initialization capabilities.
Future Integration: Exposes the primary entrypoint for acquiring loggers across all modules.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import threading

from loguru import logger

from app.core.config.config_manager import ConfigManager
from app.core.logging.handlers import configure_logging_handlers
from app.core.logging.logger import (
    redirect_standard_logging,
    register_system_exception_hook,
)


class LoggerFactory:
    """Factory to create and cache module-scoped loggers using loguru."""

    _loggers: Dict[str, Any] = {}
    _initialized: bool = False
    _lock = threading.Lock()

    @classmethod
    def initialize(cls, configs_dir: Optional[Path] = None) -> None:
        """Initializes global logging sinks using active ConfigManager configurations.

        Safe to call multiple times; will only initialize once.
        """
        with cls._lock:
            if cls._initialized:
                return

            try:
                # Load configuration dynamically to configure sinks
                config = ConfigManager(configs_dir=configs_dir).get_config()

                logs_dir = Path(config.system.logs_dir)
                log_level = config.logging.log_level
                console_logging = config.logging.console_logging
                file_logging = config.logging.file_logging
                rotation = config.logging.rotation
                retention = config.logging.retention

                # Configure loguru sinks
                configure_logging_handlers(
                    logs_dir=logs_dir,
                    log_level=log_level,
                    console_logging=console_logging,
                    file_logging=file_logging,
                    rotation=rotation,
                    retention=retention,
                )

                # Register intercepts and uncaught exception hooks
                redirect_standard_logging()
                register_system_exception_hook()

                cls._initialized = True

                # Log successful startup trace to startup.log
                startup_logger = logger.bind(module_name="LoggerFactory", startup=True)
                startup_logger.info("DriftAdapt LoggerFactory initialized successfully.")

            except Exception as e:
                # Fallback to standard console logger on failure
                logger.remove()
                logger.add(sys.stdout, level="INFO")
                logger.error(f"LoggerFactory failed to initialize: {e}")
                raise

    @classmethod
    def get_logger(cls, name: str) -> Any:
        """Retrieves or creates a module-bound logger instance.

        Args:
            name: The module or sub-module name context.

        Returns:
            A bound loguru logger instance.
        """
        if not cls._initialized:
            # Lazy initialize if not yet explicitly invoked
            cls.initialize()

        with cls._lock:
            if name not in cls._loggers:
                # Cache a logger bound with the specific module name
                cls._loggers[name] = logger.bind(module_name=name)

            return cls._loggers[name]

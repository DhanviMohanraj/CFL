"""DriftAdapt Drift Logger.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any
from app.core.logging.logger_factory import LoggerFactory


class DriftLogger:
    """Structured JSON logger for drift events."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("DriftEngine")
        
    def info(self, message: str, **kwargs: Any) -> None:
        self._logger.info(message, extra=kwargs)
        
    def warning(self, message: str, **kwargs: Any) -> None:
        self._logger.warning(message, extra=kwargs)
        
    def error(self, message: str, **kwargs: Any) -> None:
        self._logger.error(message, extra=kwargs)
        
    def debug(self, message: str, **kwargs: Any) -> None:
        self._logger.debug(message, extra=kwargs)

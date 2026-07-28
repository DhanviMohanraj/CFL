"""DriftAdapt Trainer Logger.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any

from app.core.logging.logger_factory import LoggerFactory


class TrainerLogger:
    """Structured JSON logger for local trainer events."""
    
    def __init__(self, trainer_id: str) -> None:
        self._logger = LoggerFactory.get_logger(f"Trainer-{trainer_id}")
        self._trainer_id = trainer_id
        
    def info(self, message: str, **kwargs: Any) -> None:
        self._logger.info(message, extra={"trainer_id": self._trainer_id, **kwargs})
        
    def warning(self, message: str, **kwargs: Any) -> None:
        self._logger.warning(message, extra={"trainer_id": self._trainer_id, **kwargs})
        
    def error(self, message: str, **kwargs: Any) -> None:
        self._logger.error(message, extra={"trainer_id": self._trainer_id, **kwargs})
        
    def debug(self, message: str, **kwargs: Any) -> None:
        self._logger.debug(message, extra={"trainer_id": self._trainer_id, **kwargs})

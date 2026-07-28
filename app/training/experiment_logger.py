"""DriftAdapt Experiment Logger.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any

from app.core.logging.logger_factory import LoggerFactory


class ExperimentLogger:
    """Structured JSON logger for experiment events."""
    
    def __init__(self, experiment_id: str) -> None:
        self._logger = LoggerFactory.get_logger(f"Experiment-{experiment_id}")
        self._experiment_id = experiment_id
        
    def info(self, message: str, **kwargs: Any) -> None:
        self._logger.info(message, extra={"experiment_id": self._experiment_id, **kwargs})
        
    def warning(self, message: str, **kwargs: Any) -> None:
        self._logger.warning(message, extra={"experiment_id": self._experiment_id, **kwargs})
        
    def error(self, message: str, **kwargs: Any) -> None:
        self._logger.error(message, extra={"experiment_id": self._experiment_id, **kwargs})
        
    def debug(self, message: str, **kwargs: Any) -> None:
        self._logger.debug(message, extra={"experiment_id": self._experiment_id, **kwargs})

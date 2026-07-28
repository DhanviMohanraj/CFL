"""DriftAdapt Aggregation Logger.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any
from app.core.logging.logger_factory import LoggerFactory


class AggregationLogger:
    """Structured JSON logger for aggregation events."""
    
    def __init__(self, round_id: str) -> None:
        self._logger = LoggerFactory.get_logger(f"Aggregation-{round_id}")
        self._round_id = round_id
        
    def info(self, message: str, **kwargs: Any) -> None:
        self._logger.info(message, extra={"round_id": self._round_id, **kwargs})
        
    def warning(self, message: str, **kwargs: Any) -> None:
        self._logger.warning(message, extra={"round_id": self._round_id, **kwargs})
        
    def error(self, message: str, **kwargs: Any) -> None:
        self._logger.error(message, extra={"round_id": self._round_id, **kwargs})
        
    def debug(self, message: str, **kwargs: Any) -> None:
        self._logger.debug(message, extra={"round_id": self._round_id, **kwargs})

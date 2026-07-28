"""DriftAdapt Knowledge Consolidation Logger.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any
from app.core.logging.logger_factory import LoggerFactory


class ConsolidationLogger:
    """Structured JSON logger for knowledge consolidation events."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("KnowledgeEngine")
        
    def info(self, message: str, **kwargs: Any) -> None:
        self._logger.info(message, extra=kwargs)
        
    def warning(self, message: str, **kwargs: Any) -> None:
        self._logger.warning(message, extra=kwargs)
        
    def error(self, message: str, **kwargs: Any) -> None:
        self._logger.error(message, extra=kwargs)
        
    def debug(self, message: str, **kwargs: Any) -> None:
        self._logger.debug(message, extra=kwargs)

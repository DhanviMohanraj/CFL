"""DriftAdapt Retry Manager.

Author: DriftAdapt Contributors
Purpose: Handles exponential backoff and retry policies for communication.
"""

import time
from typing import Any, Callable

from app.core.logging.logger_factory import LoggerFactory
from app.federated.communication.communication_exceptions import RetryLimitExceeded


class RetryManager:
    """Manages retries for transient communication errors."""
    
    def __init__(self, max_retries: int = 5, base_delay: float = 1.0) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay
        self._logger = LoggerFactory.get_logger("RetryManager")
        
    def execute(self, operation: Callable[..., Any], *args, **kwargs) -> Any:
        """Executes an operation with exponential backoff."""
        retries = 0
        while retries <= self.max_retries:
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                retries += 1
                if retries > self.max_retries:
                    self._logger.error(f"Operation failed after {self.max_retries} retries: {e}")
                    raise RetryLimitExceeded(f"Max retries ({self.max_retries}) exceeded: {e}") from e
                    
                delay = self.base_delay * (2 ** (retries - 1))
                self._logger.warning(f"Operation failed. Retrying in {delay}s (Attempt {retries}/{self.max_retries}). Error: {e}")
                time.sleep(delay)

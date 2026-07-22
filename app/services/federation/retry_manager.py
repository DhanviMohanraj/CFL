"""Retry Manager Service for Federated Transmission.

Author: DriftAdapt Contributors
Purpose: Manages exponential backoff and retry scheduling for failed transmissions.
"""

import time
import asyncio
from typing import Callable, Any, Awaitable

from app.core.logging import LoggerFactory


class RetryManager:
    """Manages retry policies for network operations using exponential backoff."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("RetryManager")

    async def execute_with_retry(
        self,
        operation: Callable[..., Awaitable[Any]],
        *args: Any,
        max_retries: int = 3,
        initial_backoff_s: float = 2.0,
        backoff_multiplier: float = 2.0,
        **kwargs: Any
    ) -> Any:
        """Executes an asynchronous operation with exponential backoff retries.
        
        Args:
            operation: The async function to execute.
            max_retries: Maximum number of retry attempts.
            initial_backoff_s: Initial wait time before the first retry.
            backoff_multiplier: Multiplier for subsequent backoffs.
            
        Returns:
            The result of the operation if successful.
            
        Raises:
            Exception: Re-raises the last encountered exception if retries are exhausted.
        """
        attempt = 0
        backoff = initial_backoff_s
        
        while attempt <= max_retries:
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                attempt += 1
                if attempt > max_retries:
                    self._logger.error(
                        f"Operation failed after {max_retries} retries. Final error: {str(e)}"
                    )
                    raise
                    
                self._logger.warning(
                    f"Operation failed (attempt {attempt}/{max_retries}). "
                    f"Retrying in {backoff:.1f}s... Error: {str(e)}"
                )
                
                await asyncio.sleep(backoff)
                backoff *= backoff_multiplier

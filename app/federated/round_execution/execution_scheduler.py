"""DriftAdapt Execution Scheduler.

Author: DriftAdapt Contributors
"""

import time
from typing import Callable, Any


class ExecutionScheduler:
    """Schedules execution steps and handles timeouts/retries."""
    
    def __init__(self, retry_attempts: int = 3) -> None:
        self.retry_attempts = retry_attempts
        
    def execute_with_retry(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Executes a function with retries."""
        last_exception = None
        for attempt in range(self.retry_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                time.sleep(1) # simple backoff
                
        raise last_exception

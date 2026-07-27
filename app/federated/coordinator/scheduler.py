"""DriftAdapt Scheduler.

Author: DriftAdapt Contributors
"""

import threading
from typing import Callable, List

from app.core.logging.logger_factory import LoggerFactory


class Scheduler:
    """Schedules recurring coordinator tasks."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("Scheduler")
        self._timers: List[threading.Timer] = []
        
    def schedule_task(self, interval_seconds: float, task: Callable[..., None], *args, **kwargs) -> threading.Timer:
        """Schedules a task to run after the interval."""
        timer = threading.Timer(interval_seconds, task, args=args, kwargs=kwargs)
        self._timers.append(timer)
        timer.start()
        self._logger.debug(f"Scheduled task to run in {interval_seconds}s")
        return timer
        
    def cancel_all(self) -> None:
        """Cancels all pending scheduled tasks."""
        for timer in self._timers:
            timer.cancel()
        self._timers.clear()
        self._logger.info("Cancelled all scheduled tasks.")

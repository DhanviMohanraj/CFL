"""DriftAdapt Synchronization Barrier.

Author: DriftAdapt Contributors
"""

import threading
import time

from app.core.logging.logger_factory import LoggerFactory
from app.federated.coordinator.coordinator_exceptions import SynchronizationTimeout


class SynchronizationBarrier:
    """Blocks execution until a condition is met (e.g. all uploads finished) or timeout."""
    
    def __init__(self) -> None:
        self._condition = threading.Condition()
        self._logger = LoggerFactory.get_logger("SynchronizationBarrier")
        self._is_released = False
        self._is_aborted = False
        
    def wait_for_clients(self, timeout_seconds: float) -> bool:
        """Waits until the barrier is released, aborted, or times out."""
        with self._condition:
            self._is_released = False
            self._is_aborted = False
            start_time = time.time()
            
            while not self._is_released and not self._is_aborted:
                elapsed = time.time() - start_time
                remaining = timeout_seconds - elapsed
                
                if remaining <= 0:
                    self._logger.warning("Synchronization barrier timed out.")
                    raise SynchronizationTimeout("Timed out waiting for clients.")
                    
                self._condition.wait(timeout=remaining)
                
            if self._is_aborted:
                self._logger.warning("Synchronization barrier aborted.")
                return False
                
            return True
            
    def release(self) -> None:
        """Releases the barrier, allowing execution to continue."""
        with self._condition:
            self._is_released = True
            self._condition.notify_all()
            
    def abort(self) -> None:
        """Aborts the barrier."""
        with self._condition:
            self._is_aborted = True
            self._condition.notify_all()
            
    def reset(self) -> None:
        """Resets the barrier for the next round."""
        with self._condition:
            self._is_released = False
            self._is_aborted = False

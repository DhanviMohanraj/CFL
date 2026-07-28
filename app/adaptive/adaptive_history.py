"""DriftAdapt Adaptive History.

Author: DriftAdapt Contributors
"""

import threading
from typing import List
from app.adaptive.adaptive_schema import AdaptiveRecord


class AdaptiveHistory:
    """Persists historical adaptive execution records."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._history: List[AdaptiveRecord] = []
        
    def record_execution(self, record: AdaptiveRecord) -> None:
        """Records a completed execution."""
        with self._lock:
            self._history.append(record)
            
    def get_history(self) -> List[AdaptiveRecord]:
        """Returns the recorded execution history."""
        with self._lock:
            return list(self._history)

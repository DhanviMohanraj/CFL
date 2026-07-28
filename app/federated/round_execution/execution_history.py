"""DriftAdapt Execution History.

Author: DriftAdapt Contributors
"""

import time
import threading
from typing import Dict, Any, List


class ExecutionHistory:
    """Tracks historical events for round execution."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._history: List[Dict[str, Any]] = []
        
    def record_event(self, event_type: str, details: Dict[str, Any] = None) -> None:
        """Records an execution event."""
        with self._lock:
            event = {
                "timestamp": time.time(),
                "event_type": event_type,
                "details": details or {}
            }
            self._history.append(event)
            
    def get_history(self) -> List[Dict[str, Any]]:
        """Returns the recorded event history."""
        with self._lock:
            return list(self._history)

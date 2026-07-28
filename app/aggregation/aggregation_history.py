"""DriftAdapt Aggregation History.

Author: DriftAdapt Contributors
"""

import time
import threading
from typing import Dict, Any, List


class AggregationHistory:
    """Tracks historical events for aggregation."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._history: List[Dict[str, Any]] = []
        
    def record_aggregation(self, round_id: str, algorithm: str, clients: List[str], duration: float, version: str, checksum: str, metrics: Dict[str, Any] = None) -> None:
        """Records a completed aggregation event."""
        with self._lock:
            event = {
                "timestamp": time.time(),
                "round_id": round_id,
                "algorithm": algorithm,
                "clients": clients,
                "duration": duration,
                "global_adapter_version": version,
                "checksum": checksum,
                "metrics": metrics or {}
            }
            self._history.append(event)
            
    def get_history(self) -> List[Dict[str, Any]]:
        """Returns the recorded event history."""
        with self._lock:
            return list(self._history)

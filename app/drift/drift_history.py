"""DriftAdapt Drift History.

Author: DriftAdapt Contributors
"""

import time
import threading
from typing import Dict, Any, List

from app.drift.drift_schema import DriftReport


class DriftHistory:
    """Tracks historical drift reports."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._history: List[DriftReport] = []
        
    def record_report(self, report: DriftReport) -> None:
        """Records a completed drift report."""
        with self._lock:
            self._history.append(report)
            
    def get_history(self) -> List[DriftReport]:
        """Returns the recorded event history."""
        with self._lock:
            return list(self._history)
            
    def get_clinic_history(self, clinic_id: str) -> List[DriftReport]:
        """Returns history for a specific clinic."""
        with self._lock:
            return [r for r in self._history if r.clinic_id == clinic_id]

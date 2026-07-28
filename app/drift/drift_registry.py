"""DriftAdapt Drift Registry.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, List, Optional
from app.drift.drift_schema import DriftReport


class DriftRegistry:
    """Manages tracking of recent drift reports."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._reports: Dict[str, DriftReport] = {}
        
    def register(self, report: DriftReport) -> None:
        key = f"{report.clinic_id}_{report.month}"
        with self._lock:
            self._reports[key] = report
            
    def lookup(self, clinic_id: str, month: int) -> Optional[DriftReport]:
        key = f"{clinic_id}_{month}"
        with self._lock:
            return self._reports.get(key)
            
    def history(self) -> List[DriftReport]:
        with self._lock:
            return list(self._reports.values())
            
    def statistics(self) -> Dict[str, int]:
        with self._lock:
            return {
                "total_reports": len(self._reports),
                "drifts_detected": sum(1 for r in self._reports.values() if r.drift_detected)
            }
            
    def cleanup(self) -> None:
        with self._lock:
            self._reports.clear()

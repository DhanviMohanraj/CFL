"""DriftAdapt Analytics Registry.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, List, Optional
from app.analytics.analytics_schema import AnalyticsRecord
from app.analytics.analytics_exceptions import RegistryError


class AnalyticsRegistry:
    """Maintains records of generated analytics."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._records: Dict[str, AnalyticsRecord] = {}
        
    def register(self, record: AnalyticsRecord) -> None:
        with self._lock:
            if record.record_id in self._records:
                raise RegistryError(f"Record with ID {record.record_id} already exists.")
            self._records[record.record_id] = record
            
    def lookup(self, record_id: str) -> Optional[AnalyticsRecord]:
        with self._lock:
            return self._records.get(record_id)
            
    def history(self) -> List[AnalyticsRecord]:
        with self._lock:
            return list(self._records.values())
            
    def statistics(self) -> Dict[str, int]:
        with self._lock:
            return {
                "total_records": len(self._records)
            }
            
    def cleanup(self) -> None:
        with self._lock:
            self._records.clear()

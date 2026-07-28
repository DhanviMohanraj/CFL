"""DriftAdapt Adaptive Registry.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, List, Optional
from app.adaptive.adaptive_schema import AdaptiveRecord
from app.adaptive.adaptive_exceptions import RegistryError


class AdaptiveRegistry:
    """Maintains records of adaptive aggregation executions."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._records: Dict[str, AdaptiveRecord] = {}
        
    def register(self, record: AdaptiveRecord) -> None:
        with self._lock:
            if record.adaptation_id in self._records:
                raise RegistryError(f"Record with ID {record.adaptation_id} already exists.")
            self._records[record.adaptation_id] = record
            
    def lookup(self, adaptation_id: str) -> Optional[AdaptiveRecord]:
        with self._lock:
            return self._records.get(adaptation_id)
            
    def history(self) -> List[AdaptiveRecord]:
        with self._lock:
            return list(self._records.values())
            
    def statistics(self) -> Dict[str, int]:
        with self._lock:
            return {
                "total_adaptations": len(self._records)
            }
            
    def cleanup(self) -> None:
        with self._lock:
            self._records.clear()

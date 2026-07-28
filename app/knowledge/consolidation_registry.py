"""DriftAdapt Knowledge Consolidation Registry.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, List, Optional
from app.knowledge.consolidation_schema import ConsolidationRecord
from app.knowledge.consolidation_exceptions import RegistryError


class ConsolidationRegistry:
    """Maintains records of knowledge consolidation executions."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._records: Dict[str, ConsolidationRecord] = {}
        
    def register(self, record: ConsolidationRecord) -> None:
        with self._lock:
            if record.consolidation_id in self._records:
                raise RegistryError(f"Record with ID {record.consolidation_id} already exists.")
            self._records[record.consolidation_id] = record
            
    def lookup(self, consolidation_id: str) -> Optional[ConsolidationRecord]:
        with self._lock:
            return self._records.get(consolidation_id)
            
    def history(self) -> List[ConsolidationRecord]:
        with self._lock:
            return list(self._records.values())
            
    def statistics(self) -> Dict[str, int]:
        with self._lock:
            return {
                "total_consolidations": len(self._records)
            }
            
    def cleanup(self) -> None:
        with self._lock:
            self._records.clear()

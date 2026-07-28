"""DriftAdapt Knowledge Consolidation History.

Author: DriftAdapt Contributors
"""

import threading
from typing import List
from app.knowledge.consolidation_schema import ConsolidationRecord


class ConsolidationHistory:
    """Persists historical knowledge consolidation records."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._history: List[ConsolidationRecord] = []
        
    def record_consolidation(self, record: ConsolidationRecord) -> None:
        """Records a completed consolidation."""
        with self._lock:
            self._history.append(record)
            
    def get_history(self) -> List[ConsolidationRecord]:
        """Returns the recorded consolidation history."""
        with self._lock:
            return list(self._history)

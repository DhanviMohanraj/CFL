"""DriftAdapt Benchmark Registry.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, List, Optional
from app.evaluation.evaluation_schema import EvaluationRecord
from app.evaluation.evaluation_exceptions import RegistryError


class BenchmarkRegistry:
    """Maintains records of executed benchmarks."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._records: Dict[str, EvaluationRecord] = {}
        
    def register(self, record: EvaluationRecord) -> None:
        with self._lock:
            if record.evaluation_id in self._records:
                raise RegistryError(f"Record with ID {record.evaluation_id} already exists.")
            self._records[record.evaluation_id] = record
            
    def lookup(self, record_id: str) -> Optional[EvaluationRecord]:
        with self._lock:
            return self._records.get(record_id)
            
    def history(self) -> List[EvaluationRecord]:
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

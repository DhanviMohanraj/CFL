"""DriftAdapt Aggregation Registry.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, List, Optional
from app.aggregation.aggregation_schema import AggregationMetadata


class AggregationRegistry:
    """Manages tracking of aggregation events and global adapters."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._historical_aggregations: Dict[str, AggregationMetadata] = {}
        
    def register(self, metadata: AggregationMetadata) -> None:
        with self._lock:
            self._historical_aggregations[metadata.round_id] = metadata
            
    def lookup(self, round_id: str) -> Optional[AggregationMetadata]:
        with self._lock:
            return self._historical_aggregations.get(round_id)
            
    def history(self) -> List[AggregationMetadata]:
        with self._lock:
            return list(self._historical_aggregations.values())
            
    def statistics(self) -> Dict[str, int]:
        with self._lock:
            return {
                "total_aggregations": len(self._historical_aggregations)
            }
            
    def cleanup(self) -> None:
        with self._lock:
            self._historical_aggregations.clear()

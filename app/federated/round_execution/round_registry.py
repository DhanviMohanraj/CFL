"""DriftAdapt Round Registry.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, List, Optional
from app.federated.round_execution.execution_schema import RoundMetadata


class RoundRegistry:
    """Manages active, historical, and archived rounds."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._active_rounds: Dict[str, RoundMetadata] = {}
        self._historical_rounds: Dict[str, RoundMetadata] = {}
        
    def register(self, metadata: RoundMetadata) -> None:
        with self._lock:
            self._active_rounds[metadata.round_id] = metadata
            
    def lookup(self, round_id: str) -> Optional[RoundMetadata]:
        with self._lock:
            if round_id in self._active_rounds:
                return self._active_rounds[round_id]
            return self._historical_rounds.get(round_id)
            
    def archive(self, round_id: str) -> None:
        with self._lock:
            metadata = self._active_rounds.pop(round_id, None)
            if metadata:
                self._historical_rounds[round_id] = metadata
                
    def history(self) -> List[RoundMetadata]:
        with self._lock:
            return list(self._historical_rounds.values())
            
    def statistics(self) -> Dict[str, int]:
        with self._lock:
            return {
                "active_rounds": len(self._active_rounds),
                "historical_rounds": len(self._historical_rounds)
            }
            
    def cleanup(self) -> None:
        with self._lock:
            self._active_rounds.clear()
            self._historical_rounds.clear()

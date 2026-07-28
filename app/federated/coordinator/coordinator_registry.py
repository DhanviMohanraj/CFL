"""DriftAdapt Coordinator Registry.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, List, Optional

from app.federated.coordinator.coordinator_schema import FederatedRoundMetadata, CoordinatorStatistics


class CoordinatorRegistry:
    """Thread-safe registry for federated round state and history."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._active_rounds: Dict[str, FederatedRoundMetadata] = {}
        self._historical_rounds: List[FederatedRoundMetadata] = []
        self._stats = CoordinatorStatistics()
        
    def register_round(self, round_meta: FederatedRoundMetadata) -> None:
        with self._lock:
            self._active_rounds[round_meta.round_id] = round_meta
            
    def lookup_round(self, round_id: str) -> Optional[FederatedRoundMetadata]:
        with self._lock:
            return self._active_rounds.get(round_id)
            
    def finalize_round(self, round_id: str, success: bool) -> None:
        with self._lock:
            round_meta = self._active_rounds.pop(round_id, None)
            if round_meta:
                self._historical_rounds.append(round_meta)
                self._stats.total_rounds += 1
                if success:
                    self._stats.successful_rounds += 1
                else:
                    self._stats.failed_rounds += 1
                    
                self._stats.total_client_participations += len(round_meta.completed_clients)
                self._stats.total_client_failures += len(round_meta.failed_clients)
                
    def history(self) -> List[FederatedRoundMetadata]:
        with self._lock:
            return list(self._historical_rounds)
            
    def statistics(self) -> CoordinatorStatistics:
        with self._lock:
            return self._stats.model_copy()
            
    def cleanup(self) -> None:
        with self._lock:
            self._active_rounds.clear()
            self._historical_rounds.clear()
            self._stats = CoordinatorStatistics()

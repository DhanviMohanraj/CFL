"""DriftAdapt Participation Tracker.

Author: DriftAdapt Contributors
"""

import threading

from app.federated.coordinator.coordinator_schema import FederatedRoundMetadata


class ParticipationTracker:
    """Tracks active, completed, and failed clients during a round."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        
    def record_completion(self, round_meta: FederatedRoundMetadata, client_id: str) -> None:
        """Marks a client as successfully uploaded."""
        with self._lock:
            if client_id not in round_meta.completed_clients:
                round_meta.completed_clients.append(client_id)
            if client_id in round_meta.failed_clients:
                round_meta.failed_clients.remove(client_id)
                
    def record_failure(self, round_meta: FederatedRoundMetadata, client_id: str) -> None:
        """Marks a client as failed or timed out."""
        with self._lock:
            if client_id not in round_meta.failed_clients:
                round_meta.failed_clients.append(client_id)
                
    def get_dropout_rate(self, round_meta: FederatedRoundMetadata) -> float:
        """Calculates current dropout rate for the round."""
        with self._lock:
            total_selected = len(round_meta.selected_clients)
            if total_selected == 0:
                return 0.0
            return len(round_meta.failed_clients) / total_selected
            
    def get_participation_rate(self, round_meta: FederatedRoundMetadata) -> float:
        """Calculates current successful participation rate."""
        with self._lock:
            total_selected = len(round_meta.selected_clients)
            if total_selected == 0:
                return 0.0
            return len(round_meta.completed_clients) / total_selected

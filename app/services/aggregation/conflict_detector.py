"""Conflict Detector Service.

Author: DriftAdapt Contributors
Purpose: Detects conflicts at a higher aggregation level (version mismatches, severe outliers).
"""

from typing import List, Dict, Any, Optional

from app.core.logging import LoggerFactory
from app.schemas.client_update_record import ClientUpdateRecord


class ConflictDetector:
    """Analyzes a batch of updates for fundamental conflicts that prevent aggregation."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("ConflictDetector")

    def detect_conflicts(
        self,
        updates: List[ClientUpdateRecord],
        current_global_round: int
    ) -> List[str]:
        """Detects versioning or structural conflicts in the update pool.
        
        Args:
            updates: The pool of updates.
            current_global_round: The current global round on the server.
            
        Returns:
            A list of conflict error messages. Empty if no conflicts.
        """
        conflicts = []
        
        if not updates:
            return ["No updates provided for conflict detection."]
            
        # Detect if all updates are targeting an old or future round
        rounds = {u.personalization_round for u in updates}
        if current_global_round not in rounds and len(rounds) > 0:
            conflicts.append(f"Updates target rounds {rounds}, but server is on round {current_global_round}.")
            
        # Detect severely divergent dataset sizes (potential malicious or erroneous client)
        if len(updates) > 2:
            sizes = [u.dataset_size for u in updates if u.dataset_size > 0]
            if sizes:
                mean_size = sum(sizes) / len(sizes)
                for u in updates:
                    if u.dataset_size > mean_size * 100:
                        conflicts.append(f"Client {u.client_id} reports suspiciously massive dataset ({u.dataset_size} vs mean {mean_size:.1f}).")
                        
        if conflicts:
            for c in conflicts:
                self._logger.warning(f"Conflict detected: {c}")
                
        return conflicts

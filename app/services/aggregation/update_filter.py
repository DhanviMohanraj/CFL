"""Update Filter Service.

Author: DriftAdapt Contributors
Purpose: Filters out stale, duplicated, or outlier client updates before aggregation.
"""

from typing import List, Dict, Any, Tuple

from app.core.logging import LoggerFactory
from app.schemas.client_update_record import ClientUpdateRecord


class UpdateFilter:
    """Detects and filters undesirable client updates from the aggregation pool."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("UpdateFilter")

    def filter_updates(
        self,
        updates: List[ClientUpdateRecord],
        expected_round: int
    ) -> Tuple[List[ClientUpdateRecord], List[ClientUpdateRecord]]:
        """Filters a raw list of client updates.
        
        Rules:
        - Removes duplicates (keeps the latest update per client).
        - Removes stale updates (communication round mismatch).
        
        Args:
            updates: The raw list of received update records.
            expected_round: The current federated communication round.
            
        Returns:
            A tuple of (accepted_updates, rejected_updates).
        """
        accepted: Dict[str, ClientUpdateRecord] = {}
        rejected: List[ClientUpdateRecord] = []
        
        for update in sorted(updates, key=lambda x: x.upload_timestamp):
            # 1. Stale Update Rejection
            if update.personalization_round != expected_round:
                self._logger.warning(
                    f"Rejecting stale update from {update.client_id}. "
                    f"Round {update.personalization_round} != Expected {expected_round}."
                )
                update.validation_status = "STALE"
                rejected.append(update)
                continue
                
            # 2. Duplicate Resolution (Later timestamp overrides earlier due to sorting)
            if update.client_id in accepted:
                self._logger.info(f"Overriding earlier duplicate update for client {update.client_id}.")
                old_update = accepted[update.client_id]
                old_update.validation_status = "DUPLICATE"
                rejected.append(old_update)
                
            update.validation_status = "VALID"
            accepted[update.client_id] = update
            
        accepted_list = list(accepted.values())
        return accepted_list, rejected

    def check_minimum_participation(self, valid_updates: List[ClientUpdateRecord], minimum_clients: int) -> bool:
        """Verifies if the minimum participation threshold is met."""
        met = len(valid_updates) >= minimum_clients
        if not met:
            self._logger.warning(
                f"Minimum participation not met. Have {len(valid_updates)}, need {minimum_clients}."
            )
        return met

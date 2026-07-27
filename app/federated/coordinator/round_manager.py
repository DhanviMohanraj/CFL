"""DriftAdapt Round Manager.

Author: DriftAdapt Contributors
"""

import time
import uuid
from typing import List, Optional

from app.core.logging.logger_factory import LoggerFactory
from app.federated.coordinator.coordinator_exceptions import RoundInitializationError
from app.federated.coordinator.coordinator_registry import CoordinatorRegistry
from app.federated.coordinator.coordinator_schema import FederatedRoundMetadata


class RoundManager:
    """Manages the current communication round metadata."""
    
    def __init__(self, registry: CoordinatorRegistry) -> None:
        self._registry = registry
        self._logger = LoggerFactory.get_logger("RoundManager")
        self._global_round = 0
        self._current_round: Optional[FederatedRoundMetadata] = None
        
    def begin_round(self, selected_clients: List[str]) -> FederatedRoundMetadata:
        """Initializes a new communication round."""
        if self._current_round and self._current_round.status not in ("COMPLETED", "FAILED", "CANCELLED"):
            raise RoundInitializationError("A round is already active.")
            
        self._global_round += 1
        round_id = str(uuid.uuid4())
        
        self._current_round = FederatedRoundMetadata(
            round_id=round_id,
            global_round=self._global_round,
            selected_clients=selected_clients,
            status="INITIALIZED"
        )
        
        self._registry.register_round(self._current_round)
        self._logger.info(f"Began round {self._global_round} ({round_id}) with {len(selected_clients)} clients.")
        return self._current_round
        
    def finish_round(self, success: bool) -> None:
        """Marks the current round as finished."""
        if not self._current_round:
            return
            
        self._current_round.status = "COMPLETED" if success else "FAILED"
        self._current_round.end_time = time.time()
        
        self._registry.finalize_round(self._current_round.round_id, success)
        self._logger.info(f"Finished round {self._global_round} (Success: {success})")
        self._current_round = None
        
    def current_round(self) -> Optional[FederatedRoundMetadata]:
        return self._current_round
        
    def history(self) -> List[FederatedRoundMetadata]:
        return self._registry.history()

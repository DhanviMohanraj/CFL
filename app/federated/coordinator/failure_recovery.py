"""DriftAdapt Failure Recovery.

Author: DriftAdapt Contributors
"""

from app.core.logging.logger_factory import LoggerFactory
from app.federated.coordinator.coordinator_exceptions import RoundRecoveryError
from app.federated.coordinator.coordinator_schema import FederatedRoundMetadata


class FailureRecovery:
    """Handles logic for recovering from round failures."""
    
    def __init__(self, allow_partial: bool = True) -> None:
        self._logger = LoggerFactory.get_logger("FailureRecovery")
        self._allow_partial = allow_partial
        
    def can_proceed(self, round_meta: FederatedRoundMetadata, min_clients: int) -> bool:
        """Determines if the round can proceed despite failures."""
        completed = len(round_meta.completed_clients)
        
        if completed == 0:
            self._logger.error("No clients successfully uploaded.")
            return False
            
        if completed < min_clients:
            self._logger.warning(f"Insufficient completed clients ({completed} < {min_clients}).")
            return False
            
        if len(round_meta.failed_clients) > 0 and not self._allow_partial:
            self._logger.error("Failures occurred and partial participation is disabled.")
            return False
            
        return True
        
    def recover_round(self, round_meta: FederatedRoundMetadata) -> None:
        """Attempts to salvage an interrupted round."""
        self._logger.info(f"Attempting to recover round {round_meta.round_id}...")
        # Future advanced logic: attempt re-request to failed clients, etc.
        raise RoundRecoveryError("Advanced recovery not implemented for this round.")

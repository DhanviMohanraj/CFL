"""DriftAdapt Checkpoint Orchestrator.

Author: DriftAdapt Contributors
"""

from typing import Any
from app.training.experiment_exceptions import CheckpointRecoveryError


class CheckpointOrchestrator:
    """Coordinates global and client checkpoints."""
    
    def __init__(self) -> None:
        pass
        
    def save_checkpoint(self, experiment_id: str, state: Any) -> None:
        """Mocks saving a checkpoint to disk."""
        pass
        
    def restore_checkpoint(self, experiment_id: str) -> Any:
        """Mocks restoring a checkpoint from disk."""
        # Raise error because there's no actual data in this mock
        raise CheckpointRecoveryError(f"No checkpoint found for experiment {experiment_id}")

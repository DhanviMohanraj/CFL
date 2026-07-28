"""DriftAdapt Checkpoint Scheduler.

Author: DriftAdapt Contributors
"""

import os
from typing import List, Optional

from app.core.logging.logger_factory import LoggerFactory
from app.federated.client.client_exceptions import CheckpointError
from app.federated.client.client_schema import CheckpointMetadata


class CheckpointScheduler:
    """Manages the saving and rotation of local training checkpoints."""
    
    def __init__(self, save_dir: str, max_checkpoints: int = 3) -> None:
        self._save_dir = save_dir
        self._max_checkpoints = max_checkpoints
        self._checkpoints: List[CheckpointMetadata] = []
        self._logger = LoggerFactory.get_logger("CheckpointScheduler")
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
            
    def save_checkpoint(self, epoch: int, loss: float, weights: bytes) -> CheckpointMetadata:
        """Saves a checkpoint and rotates old ones if necessary."""
        try:
            checkpoint_id = f"ckpt_epoch_{epoch}"
            path = os.path.join(self._save_dir, f"{checkpoint_id}.pt")
            
            with open(path, "wb") as f:
                f.write(weights)
                
            metadata = CheckpointMetadata(
                checkpoint_id=checkpoint_id,
                epoch=epoch,
                path=path,
                loss=loss
            )
            
            self._checkpoints.append(metadata)
            self._logger.info(f"Saved checkpoint: {path}")
            
            self._rotate()
            return metadata
        except Exception as e:
            raise CheckpointError(f"Failed to save checkpoint: {e}") from e
            
    def _rotate(self) -> None:
        """Removes oldest checkpoints exceeding max limit."""
        while len(self._checkpoints) > self._max_checkpoints:
            oldest = self._checkpoints.pop(0)
            if os.path.exists(oldest.path):
                os.remove(oldest.path)
                self._logger.debug(f"Removed old checkpoint: {oldest.path}")
                
    def get_latest(self) -> Optional[CheckpointMetadata]:
        """Returns metadata for the most recent checkpoint."""
        if not self._checkpoints:
            return None
        return self._checkpoints[-1]
        
    def clean_all(self) -> None:
        """Removes all checkpoints."""
        for ckpt in self._checkpoints:
            if os.path.exists(ckpt.path):
                os.remove(ckpt.path)
        self._checkpoints.clear()

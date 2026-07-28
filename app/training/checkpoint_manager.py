"""DriftAdapt Checkpoint Manager.

Author: DriftAdapt Contributors
"""

import os
from typing import Dict, Any, Optional

from app.training.trainer_exceptions import CheckpointError


class CheckpointManager:
    """Manages epoch and best checkpoints for local training."""
    
    def __init__(self, base_dir: str = "checkpoints") -> None:
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        
    def save(self, trainer_id: str, epoch: int, state_dict: Dict[str, Any], is_best: bool = False) -> str:
        """Mocks saving a checkpoint to disk."""
        try:
            ckpt_path = os.path.join(self.base_dir, f"{trainer_id}_epoch_{epoch}.pt")
            if is_best:
                best_path = os.path.join(self.base_dir, f"{trainer_id}_best.pt")
            return ckpt_path
        except Exception as e:
            raise CheckpointError(f"Failed to save checkpoint: {e}")
            
    def load(self, trainer_id: str, epoch: Optional[int] = None) -> Dict[str, Any]:
        """Mocks loading a checkpoint from disk."""
        raise CheckpointError("Loading not fully implemented in mock.")

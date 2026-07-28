"""DriftAdapt Checkpoint Service.

Author: DriftAdapt Contributors
Purpose: Manages persistence and restoration of LoRA adapters and optimizer states.
"""

import os
import uuid
import datetime
from typing import Optional, Any
from pathlib import Path

import torch
from peft import PeftModel
from torch.optim import Optimizer
from torch.optim.lr_scheduler import LRScheduler

from app.schemas.training_checkpoint import TrainingCheckpoint
from app.core.logging import LoggerFactory


class CheckpointService:
    """Service handling disk I/O for model checkpoints and states."""

    def __init__(self, checkpoint_dir: str = "./checkpoints") -> None:
        self._logger = LoggerFactory.get_logger("CheckpointService")
        self._checkpoint_dir = Path(checkpoint_dir)
        self._checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(
        self,
        model: PeftModel,
        optimizer: Optional[Optimizer],
        scheduler: Optional[LRScheduler],
        adapter_id: str,
        epoch: float,
        training_round: int
    ) -> TrainingCheckpoint:
        """Saves the PEFT adapter weights and optimizer states.
        
        Args:
            model: The PEFT model to save.
            optimizer: PyTorch optimizer (optional).
            scheduler: Learning rate scheduler (optional).
            adapter_id: ID of the adapter.
            epoch: Current training epoch.
            training_round: Continual learning round.
            
        Returns:
            TrainingCheckpoint metadata.
        """
        checkpoint_id = str(uuid.uuid4())
        save_path = self._checkpoint_dir / adapter_id / f"checkpoint-{checkpoint_id}"
        save_path.mkdir(parents=True, exist_ok=True)

        self._logger.info(f"Saving checkpoint to {save_path}")
        
        # Save PEFT adapter weights only (not base model)
        model.save_pretrained(str(save_path))

        # Save optimizer state
        opt_saved = False
        if optimizer is not None:
            torch.save(optimizer.state_dict(), save_path / "optimizer.pt")
            opt_saved = True

        # Save scheduler state
        sched_saved = False
        if scheduler is not None:
            torch.save(scheduler.state_dict(), save_path / "scheduler.pt")
            sched_saved = True

        return TrainingCheckpoint(
            checkpoint_id=checkpoint_id,
            adapter_id=adapter_id,
            epoch=epoch,
            optimizer_state_saved=opt_saved,
            scheduler_state_saved=sched_saved,
            model_state_saved=True,
            timestamp=datetime.datetime.utcnow().isoformat(),
            training_round=training_round,
            file_path=str(save_path)
        )

    def load_states(self, checkpoint_path: str, optimizer: Optimizer, scheduler: Optional[LRScheduler]) -> None:
        """Restores optimizer and scheduler states from a checkpoint directory.
        
        Note: The PEFT model weights should be loaded via PEFTManager.from_pretrained.
        """
        path = Path(checkpoint_path)
        opt_path = path / "optimizer.pt"
        if opt_path.exists():
            optimizer.load_state_dict(torch.load(opt_path))
            self._logger.info("Restored optimizer state.")

        if scheduler is not None:
            sched_path = path / "scheduler.pt"
            if sched_path.exists():
                scheduler.load_state_dict(torch.load(sched_path))
                self._logger.info("Restored scheduler state.")

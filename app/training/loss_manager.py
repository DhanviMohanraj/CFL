"""DriftAdapt Loss Manager.

Author: DriftAdapt Contributors
"""

import torch
import torch.nn as nn
from typing import Dict, Any


class LossManager:
    """Computes and tracks training and validation losses."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.criterion = nn.CrossEntropyLoss()
        
        self.train_loss_history = []
        self.val_loss_history = []
        
        self._current_epoch_train_losses = []
        
    def compute_loss(self, outputs, targets) -> torch.Tensor:
        """Computes the loss for a batch."""
        loss = self.criterion(outputs.view(-1, outputs.size(-1)), targets.view(-1))
        self._current_epoch_train_losses.append(loss.item())
        return loss
        
    def get_epoch_train_loss(self) -> float:
        """Returns the average training loss for the current epoch."""
        if not self._current_epoch_train_losses:
            return 0.0
        avg_loss = sum(self._current_epoch_train_losses) / len(self._current_epoch_train_losses)
        self.train_loss_history.append(avg_loss)
        self._current_epoch_train_losses = []
        return avg_loss

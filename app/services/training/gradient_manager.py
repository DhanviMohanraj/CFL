"""DriftAdapt Gradient Manager.

Author: DriftAdapt Contributors
Purpose: Handles advanced gradient operations including scaling, clipping, and mixed precision.
"""

from typing import Dict, Any
import torch
from torch.nn import Module
from torch.optim import Optimizer
from torch.amp import GradScaler

from app.schemas.training_config import TrainingConfiguration
from app.core.logging import LoggerFactory


class GradientManager:
    """Service responsible for managing gradients during the backward pass."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("GradientManager")
        self._scaler = GradScaler('cuda')

    def backward(self, loss: torch.Tensor, config: TrainingConfiguration) -> None:
        """Performs the backward pass, utilizing automatic mixed precision if enabled.

        Args:
            loss: The computed scalar loss tensor.
            config: Training configuration specifying mixed precision and accumulation.
        """
        # Scale loss by accumulation steps
        loss = loss / config.gradient_accumulation_steps

        if config.mixed_precision and torch.cuda.is_available():
            self._scaler.scale(loss).backward()
        else:
            loss.backward()

    def step(self, model: Module, optimizer: Optimizer, config: TrainingConfiguration) -> Dict[str, Any]:
        """Performs gradient clipping and the optimizer step.

        Args:
            model: The neural network model.
            optimizer: The PyTorch optimizer.
            config: Training configuration specifying max grad norm.

        Returns:
            Dictionary containing gradient statistics.
        """
        if config.mixed_precision and torch.cuda.is_available():
            self._scaler.unscale_(optimizer)

        # Compute gradient norm for monitoring
        grad_norm = torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            config.max_grad_norm
        )

        # Check for NaN gradients
        if torch.isnan(grad_norm) or torch.isinf(grad_norm):
            self._logger.warning("NaN or Inf gradients detected. Skipping optimization step.")
            optimizer.zero_grad()
            return {"grad_norm": grad_norm.item(), "step_skipped": True}

        if config.mixed_precision and torch.cuda.is_available():
            self._scaler.step(optimizer)
            self._scaler.update()
        else:
            optimizer.step()

        optimizer.zero_grad()
        return {"grad_norm": grad_norm.item(), "step_skipped": False}

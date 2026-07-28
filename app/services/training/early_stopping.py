"""DriftAdapt Early Stopping Service.

Author: DriftAdapt Contributors
Purpose: Monitors validation loss and triggers early termination if no improvement occurs.
"""

from typing import Tuple
from app.core.logging import LoggerFactory


class EarlyStoppingService:
    """Service to halt training prematurely based on validation metrics."""

    def __init__(self, patience: int = 3, min_delta: float = 1e-4) -> None:
        """Initializes the EarlyStoppingService.

        Args:
            patience: Number of epochs to wait for improvement before stopping.
            min_delta: Minimum change in loss to qualify as an improvement.
        """
        self._logger = LoggerFactory.get_logger("EarlyStoppingService")
        self._patience = patience
        self._min_delta = min_delta
        self._best_loss = float('inf')
        self._counter = 0
        self._early_stop = False

    def step(self, validation_loss: float) -> Tuple[bool, bool]:
        """Processes the latest validation loss.

        Args:
            validation_loss: The latest loss on the validation set.

        Returns:
            A tuple (is_best, should_stop).
        """
        is_best = False

        if validation_loss < self._best_loss - self._min_delta:
            self._best_loss = validation_loss
            self._counter = 0
            is_best = True
            self._logger.info(f"Validation loss improved to {validation_loss:.4f}.")
        else:
            self._counter += 1
            self._logger.info(f"No improvement. Early stopping counter: {self._counter}/{self._patience}")
            if self._counter >= self._patience:
                self._early_stop = True
                self._logger.warning("Early stopping triggered due to lack of improvement.")

        return is_best, self._early_stop

    def reset(self) -> None:
        """Resets the early stopping state for a new training run."""
        self._best_loss = float('inf')
        self._counter = 0
        self._early_stop = False

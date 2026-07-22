"""DriftAdapt Training Metrics Service.

Author: DriftAdapt Contributors
Purpose: Aggregates and stores epoch-level metrics history for a personalization run.
"""

from typing import List
from app.schemas.training_metrics import TrainingMetrics
from app.core.logging import LoggerFactory


class MetricsService:
    """Service to track and compute historical training metrics."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("MetricsService")
        self._history: List[TrainingMetrics] = []

    def record_metrics(self, metrics: TrainingMetrics) -> None:
        """Saves a metric snapshot.

        Args:
            metrics: The validated TrainingMetrics object.
        """
        self._history.append(metrics)
        self._logger.info(
            f"Epoch {metrics.epoch:.2f} | "
            f"Train Loss: {metrics.training_loss:.4f} | "
            f"Val Loss: {metrics.validation_loss if metrics.validation_loss else 'N/A'}"
        )

    def get_history(self) -> List[TrainingMetrics]:
        """Returns the full metrics history."""
        return self._history

    def get_best_loss(self) -> float:
        """Finds the lowest validation loss recorded."""
        val_losses = [m.validation_loss for m in self._history if m.validation_loss is not None]
        if val_losses:
            return min(val_losses)

        train_losses = [m.training_loss for m in self._history]
        if train_losses:
            return min(train_losses)

        return float('inf')

    def clear(self) -> None:
        """Clears the metrics history."""
        self._history.clear()

"""DriftAdapt Training History.

Author: DriftAdapt Contributors
"""

import json
from typing import List

from app.core.logging.logger_factory import LoggerFactory
from app.federated.client.client_schema import TrainingEpochResult


class TrainingHistory:
    """Tracks training epochs and validation scores locally."""
    
    def __init__(self) -> None:
        self._epochs: List[TrainingEpochResult] = []
        self._logger = LoggerFactory.get_logger("TrainingHistory")
        
    def add_epoch(self, epoch: int, loss: float, validation_score: float = 0.0) -> None:
        result = TrainingEpochResult(
            epoch=epoch,
            loss=loss,
            validation_score=validation_score
        )
        self._epochs.append(result)
        self._logger.debug(f"Recorded epoch {epoch}: loss={loss:.4f}, val={validation_score:.4f}")
        
    def get_history(self) -> List[TrainingEpochResult]:
        return list(self._epochs)
        
    def export_json(self) -> str:
        """Exports the entire training history as a JSON string."""
        return json.dumps([e.model_dump() for e in self._epochs], indent=2)
        
    def clear(self) -> None:
        self._epochs.clear()

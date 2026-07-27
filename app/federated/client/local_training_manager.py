"""DriftAdapt Local Training Manager.

Author: DriftAdapt Contributors
"""

from typing import Callable, Optional

from app.core.logging.logger_factory import LoggerFactory
from app.federated.client.client_exceptions import TrainingSessionError
from app.federated.client.training_history import TrainingHistory


class LocalTrainingManager:
    """Manages the execution of local LoRA training epochs."""
    
    def __init__(self, history: TrainingHistory, max_epochs: int = 5, validation_interval: int = 1) -> None:
        self._history = history
        self._max_epochs = max_epochs
        self._validation_interval = validation_interval
        self._logger = LoggerFactory.get_logger("LocalTrainingManager")
        self._current_epoch = 0
        
    def train(self, 
              training_step_fn: Callable[[], float], 
              validation_step_fn: Optional[Callable[[], float]] = None,
              checkpoint_fn: Optional[Callable[[int, float], None]] = None) -> None:
        """Executes the training loop."""
        self._logger.info(f"Starting training for {self._max_epochs} epochs.")
        
        try:
            for epoch in range(1, self._max_epochs + 1):
                self._current_epoch = epoch
                
                # Simulate / execute training step
                loss = training_step_fn()
                
                # Simulate / execute validation step
                val_score = 0.0
                if validation_step_fn and epoch % self._validation_interval == 0:
                    val_score = validation_step_fn()
                    
                self._history.add_epoch(epoch, loss, val_score)
                
                # Checkpoint
                if checkpoint_fn:
                    checkpoint_fn(epoch, loss)
                    
            self._logger.info("Training completed successfully.")
        except Exception as e:
            self._logger.error(f"Training failed at epoch {self._current_epoch}: {e}")
            raise TrainingSessionError(f"Training failed: {e}") from e

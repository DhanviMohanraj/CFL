"""DriftAdapt Training Orchestrator.

Author: DriftAdapt Contributors
"""

from typing import Optional

from app.core.logging.logger_factory import LoggerFactory
from app.federated.client.checkpoint_scheduler import CheckpointScheduler
from app.federated.client.client_exceptions import TrainingInterruptedError, TrainingSessionError
from app.federated.client.local_training_manager import LocalTrainingManager


class TrainingOrchestrator:
    """High-level orchestrator linking dataset, model, and training execution."""
    
    def __init__(self, training_manager: LocalTrainingManager, checkpoint_scheduler: CheckpointScheduler) -> None:
        self._training_manager = training_manager
        self._checkpoint_scheduler = checkpoint_scheduler
        self._logger = LoggerFactory.get_logger("TrainingOrchestrator")
        self._active_weights: Optional[bytes] = None
        self._is_aborted: bool = False
        
    def prepare_training(self) -> None:
        """Prepares datasets and initializes model for training."""
        self._is_aborted = False
        self._logger.info("Prepared resources for training.")
        
    def begin_training(self) -> None:
        """Executes the training process."""
        if self._is_aborted:
            raise TrainingInterruptedError("Training was aborted before it began.")
            
        def mock_train_step() -> float:
            if self._is_aborted:
                raise TrainingInterruptedError("Training aborted by user.")
            return 0.5  # Mock loss
            
        def mock_val_step() -> float:
            return 0.8  # Mock validation score
            
        def ckpt_step(epoch: int, loss: float) -> None:
            self._checkpoint_scheduler.save_checkpoint(epoch, loss, b"dummy_weights")
            
        self._training_manager.train(
            training_step_fn=mock_train_step,
            validation_step_fn=mock_val_step,
            checkpoint_fn=ckpt_step
        )
        self._active_weights = b"trained_weights"
        
    def abort_training(self) -> None:
        """Aborts the currently running training."""
        self._is_aborted = True
        self._logger.warning("Training aborted.")
        
    def finish_training(self) -> None:
        """Cleans up resources after training."""
        self._logger.info("Finished training and cleaned up.")
        
    def export_adapter(self) -> bytes:
        """Exports the trained adapter weights."""
        if not self._active_weights:
            raise TrainingSessionError("No active weights to export. Was training completed?")
        self._logger.info("Exported trained adapter.")
        return self._active_weights

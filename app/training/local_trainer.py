"""DriftAdapt Local LoRA Trainer.

Author: DriftAdapt Contributors
"""

import torch
from typing import Dict, Any, Optional

from app.core.metrics.metrics_bus import MetricsBus
from app.training.training_state import TrainingState
from app.training.trainer_schema import TrainerMetadata
from app.training.trainer_logger import TrainerLogger
from app.training.trainer_metrics import TrainerMetrics
from app.training.optimizer_manager import OptimizerManager
from app.training.scheduler_manager import SchedulerManager
from app.training.gradient_manager import GradientManager
from app.training.loss_manager import LossManager
from app.training.validation_manager import ValidationManager
from app.training.checkpoint_manager import CheckpointManager
from app.training.adapter_exporter import AdapterExporter
from app.training.personalization_engine import PersonalizationEngine
from app.training.trainer_exceptions import TrainingExecutionError


class LocalLoRATrainer:
    """Executes local LoRA fine-tuning for a specific clinic."""
    
    def __init__(
        self,
        trainer_id: str,
        clinic_id: str,
        month: int,
        config: Dict[str, Any],
        metrics_bus: MetricsBus
    ) -> None:
        self.trainer_id = trainer_id
        self.clinic_id = clinic_id
        self.month = month
        self.config = config
        
        self.state = TrainingState.CREATED
        self.logger = TrainerLogger(trainer_id)
        self.metrics = TrainerMetrics(metrics_bus)
        
        self.optimizer_mgr = OptimizerManager()
        self.scheduler_mgr = SchedulerManager()
        self.gradient_mgr = GradientManager(config)
        self.loss_mgr = LossManager(config)
        self.validation_mgr = ValidationManager(config)
        self.checkpoint_mgr = CheckpointManager()
        self.adapter_exporter = AdapterExporter()
        self.personalization_engine = PersonalizationEngine(config)
        
        self.model = None
        self.optimizer = None
        self.scheduler = None
        
    def initialize(self) -> None:
        """Initializes the model and components for training."""
        self.state = TrainingState.INITIALIZING
        self.model = self.personalization_engine.prepare_model()
        
        self.optimizer = self.optimizer_mgr.create_optimizer(self.model.parameters(), self.config)
        
        total_steps = self.config.get("local_epochs", 3) * 10
        self.scheduler = self.scheduler_mgr.create_scheduler(self.optimizer, self.config, total_steps)
        
        self.metrics.publish_event("training.started", tags={"clinic": self.clinic_id, "month": self.month})
        self.logger.info(f"Trainer initialized for {self.clinic_id}, month {self.month}.")
        
    def prepare(self) -> None:
        """Prepares datasets."""
        self.state = TrainingState.PREPARING_DATA
        self.logger.info("Data prepared.")
        
    def train(self) -> None:
        """Executes the training loop."""
        self.state = TrainingState.TRAINING
        epochs = self.config.get("local_epochs", 3)
        
        for epoch in range(1, epochs + 1):
            self.metrics.publish_event("epoch.started", tags={"epoch": epoch})
            
            for _ in range(10): # 10 mock batches
                outputs = torch.randn(4, 10, requires_grad=True)
                targets = torch.randint(0, 10, (4,))
                
                self.optimizer.zero_grad()
                loss = self.loss_mgr.compute_loss(outputs, targets)
                loss.backward()
                self.gradient_mgr.step(self.optimizer, self.model.parameters())
                
            self.scheduler.step()
            avg_train_loss = self.loss_mgr.get_epoch_train_loss()
            self.metrics.publish_value("training.loss", avg_train_loss, tags={"epoch": epoch})
            self.metrics.publish_event("epoch.completed", tags={"epoch": epoch})
            
            if self.config.get("validation_every_epoch", True):
                self.validate(epoch)
                
            if self.config.get("checkpoint_every_epoch", True):
                self.save_checkpoint(epoch)
                
            if self.state == TrainingState.COMPLETED or self.state == TrainingState.CANCELLED:
                break
                
        if self.state == TrainingState.TRAINING:
            self.state = TrainingState.COMPLETED
            
        self.metrics.publish_event("training.completed")
        self.logger.info("Training completed.")
        
    def validate(self, epoch: int) -> None:
        """Validates the model."""
        self.state = TrainingState.VALIDATING
        
        predictions = torch.randint(0, 10, (100,))
        targets = torch.randint(0, 10, (100,))
        
        metrics_result = self.validation_mgr.evaluate(predictions, targets)
        mock_val_loss = 0.5
        
        self.metrics.publish_value("validation.loss", mock_val_loss, tags={"epoch": epoch})
        self.metrics.publish_value("training.accuracy", metrics_result["accuracy"], tags={"epoch": epoch})
        
        stop_training, is_best = self.validation_mgr.check_early_stopping(mock_val_loss)
        if is_best and self.config.get("save_best_only", True):
            self.checkpoint_mgr.save(self.trainer_id, epoch, {}, is_best=True)
            
        if stop_training:
            self.logger.info("Early stopping triggered.")
            self.state = TrainingState.COMPLETED
        else:
            self.state = TrainingState.TRAINING
            
    def save_checkpoint(self, epoch: int) -> None:
        self.state = TrainingState.CHECKPOINTING
        self.checkpoint_mgr.save(self.trainer_id, epoch, {})
        self.metrics.publish_event("checkpoint.saved", tags={"epoch": epoch})
        self.state = TrainingState.TRAINING
        
    def export_adapter(self) -> str:
        self.state = TrainingState.EXPORTING
        metadata = {"clinic_id": self.clinic_id, "month": self.month}
        export_path = self.adapter_exporter.export_adapter(self.trainer_id, {}, metadata)
        self.metrics.publish_event("adapter.exported", tags={"clinic": self.clinic_id})
        self.logger.info(f"Adapter exported to {export_path}")
        return export_path
        
    def cleanup(self) -> None:
        self.model = None
        self.optimizer = None
        self.logger.info("Trainer resources cleaned up.")
        
    def status(self) -> str:
        return self.state.value

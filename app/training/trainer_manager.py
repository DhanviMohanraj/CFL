"""DriftAdapt Trainer Manager.

Author: DriftAdapt Contributors
"""

import uuid
from typing import Dict, Any, Optional

from app.core.metrics.metrics_bus import MetricsBus
from app.training.trainer_schema import TrainerMetadata
from app.training.trainer_registry import TrainerRegistry
from app.training.trainer_factory import TrainerFactory


class TrainerManager:
    """Manages the lifecycle of multiple local trainers."""
    
    def __init__(self, registry: TrainerRegistry, metrics_bus: MetricsBus) -> None:
        self.registry = registry
        self.factory = TrainerFactory(metrics_bus)
        self.active_trainers = {}
        
    def create_trainer(self, clinic_id: str, month: int, config: Dict[str, Any]) -> str:
        trainer_id = str(uuid.uuid4())
        trainer = self.factory.create_trainer(trainer_id, clinic_id, month, config)
        
        metadata = TrainerMetadata(
            trainer_id=trainer_id,
            clinic_id=clinic_id,
            month=month,
            config=config,
            status=trainer.status()
        )
        
        self.registry.register(metadata)
        self.active_trainers[trainer_id] = trainer
        return trainer_id
        
    def start_training(self, trainer_id: str) -> None:
        trainer = self.active_trainers.get(trainer_id)
        if trainer:
            trainer.initialize()
            trainer.prepare()
            trainer.train()
            trainer.export_adapter()
            trainer.cleanup()
            
            metadata = self.registry.lookup(trainer_id)
            if metadata:
                metadata.status = trainer.status()
                
    def get_trainer_status(self, trainer_id: str) -> Optional[str]:
        metadata = self.registry.lookup(trainer_id)
        return metadata.status if metadata else None

"""DriftAdapt Trainer Factory.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any

from app.core.metrics.metrics_bus import MetricsBus
from app.training.local_trainer import LocalLoRATrainer


class TrainerFactory:
    """Creates instances of local trainers."""
    
    def __init__(self, metrics_bus: MetricsBus) -> None:
        self.metrics_bus = metrics_bus
        
    def create_trainer(self, trainer_id: str, clinic_id: str, month: int, config: Dict[str, Any]) -> LocalLoRATrainer:
        return LocalLoRATrainer(trainer_id, clinic_id, month, config, self.metrics_bus)

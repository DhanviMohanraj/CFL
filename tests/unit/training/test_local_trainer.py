"""Tests for Local Trainer.

Author: DriftAdapt Contributors
"""

from app.core.metrics.metrics_bus import MetricsBus
from app.training.local_trainer import LocalLoRATrainer
from app.training.training_state import TrainingState


def test_local_trainer():
    bus = MetricsBus()
    config = {
        "local_epochs": 1,
        "batch_size": 4,
        "learning_rate": 1e-4,
        "gradient_clipping": 0.0,
        "mixed_precision": False,
        "save_best_only": False,
        "optimizer": "adamw",
        "scheduler": "constant"
    }
    
    trainer = LocalLoRATrainer("trainer_1", "clinic_01", 1, config, bus)
    
    assert trainer.status() == TrainingState.CREATED.value
    
    trainer.initialize()
    assert trainer.status() == TrainingState.INITIALIZING.value
    
    trainer.prepare()
    assert trainer.status() == TrainingState.PREPARING_DATA.value
    
    trainer.train()
    assert trainer.status() == TrainingState.COMPLETED.value
    
    path = trainer.export_adapter()
    assert path is not None
    
    trainer.cleanup()
    assert trainer.model is None

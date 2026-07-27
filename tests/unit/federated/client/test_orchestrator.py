"""Tests for Training Orchestrator.

Author: DriftAdapt Contributors
"""

import pytest

from app.federated.client.training_orchestrator import TrainingOrchestrator
from app.federated.client.local_training_manager import LocalTrainingManager
from app.federated.client.checkpoint_scheduler import CheckpointScheduler
from app.federated.client.training_history import TrainingHistory


def test_orchestrator_full_flow(tmp_path):
    history = TrainingHistory()
    training_mgr = LocalTrainingManager(history, max_epochs=2)
    ckpt_scheduler = CheckpointScheduler(str(tmp_path))
    
    orchestrator = TrainingOrchestrator(training_mgr, ckpt_scheduler)
    
    orchestrator.prepare_training()
    orchestrator.begin_training()
    
    weights = orchestrator.export_adapter()
    assert weights == b"trained_weights"
    
    orchestrator.finish_training()

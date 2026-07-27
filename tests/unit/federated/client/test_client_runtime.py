"""Tests for Client Runtime.

Author: DriftAdapt Contributors
"""

import pytest

from app.federated.client.client_registry import ClientRegistry
from app.federated.client.client_runtime import ClientRuntime
from app.federated.client.training_orchestrator import TrainingOrchestrator
from app.federated.client.local_training_manager import LocalTrainingManager
from app.federated.client.checkpoint_scheduler import CheckpointScheduler
from app.federated.client.training_history import TrainingHistory
from app.federated.client.runtime_state import RuntimeState


def test_client_runtime_lifecycle(tmp_path):
    registry = ClientRegistry()
    history = TrainingHistory()
    training_mgr = LocalTrainingManager(history, max_epochs=2)
    ckpt_scheduler = CheckpointScheduler(str(tmp_path))
    orchestrator = TrainingOrchestrator(training_mgr, ckpt_scheduler)
    
    runtime = ClientRuntime("clinic_1", orchestrator, registry)
    
    runtime.initialize()
    assert registry.lookup("clinic_1") is not None
    
    assert runtime.status() == RuntimeState.IDLE.value
    
    runtime.start(round_num=1)
    
    assert runtime.status() == RuntimeState.COMPLETED.value
    
    runtime.shutdown()
    assert registry.lookup("clinic_1") is None

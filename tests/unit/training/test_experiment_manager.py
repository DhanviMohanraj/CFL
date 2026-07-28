"""Tests for Experiment Manager.

Author: DriftAdapt Contributors
"""

import pytest
from app.training.experiment_manager import ExperimentManager
from app.training.experiment_registry import ExperimentRegistry
from app.training.training_configuration import TrainingConfiguration


def test_experiment_manager_lifecycle():
    registry = ExperimentRegistry()
    manager = ExperimentManager(registry)
    config = TrainingConfiguration()
    
    exp_id = manager.create(config)
    assert manager.status() == "CREATED"
    
    manager.start(exp_id)
    assert manager.status() == "STARTED"
    
    manager.pause(exp_id)
    assert manager.status() == "PAUSED"
    
    manager.resume(exp_id)
    assert manager.status() == "STARTED"
    
    manager.terminate(exp_id, success=True)
    assert manager.status() == "COMPLETED"
    
    manager.archive(exp_id)
    assert registry.lookup(exp_id) is not None

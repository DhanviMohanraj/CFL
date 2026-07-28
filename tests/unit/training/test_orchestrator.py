"""Tests for Experiment Orchestrator.

Author: DriftAdapt Contributors
"""

import pytest
from app.training.orchestrator import FederatedTrainingOrchestrator
from app.training.training_configuration import TrainingConfiguration


def test_orchestrator_initialization():
    config = TrainingConfiguration(total_months=2, communication_rounds=2)
    orchestrator = FederatedTrainingOrchestrator(config)
    orchestrator.initialize()
    
    assert orchestrator._experiment_id is not None
    assert orchestrator._lifecycle._state_machine.current_state.value == "INITIALIZING"

def test_orchestrator_run_experiment():
    config = TrainingConfiguration(total_months=1, communication_rounds=1)
    orchestrator = FederatedTrainingOrchestrator(config)
    orchestrator.initialize()
    
    orchestrator._lifecycle._state_machine.transition_to("PREPARING")
    
    clinics = ["clinic_01", "clinic_02"]
    orchestrator.run_experiment(clinics)
    
    assert orchestrator._experiment_scheduler.is_complete()
    assert orchestrator._progress.completed_months == 1
    assert orchestrator._progress.completed_rounds == 1
    
    assert orchestrator._lifecycle._state_machine.current_state.value == "COMPLETED"

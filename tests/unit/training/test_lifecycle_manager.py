"""Tests for Lifecycle Manager.

Author: DriftAdapt Contributors
"""

from app.training.lifecycle_manager import LifecycleManager
from app.training.state_machine import StateMachine
from app.training.experiment_state import ExperimentState


def test_lifecycle_manager():
    sm = StateMachine()
    manager = LifecycleManager(sm)
    
    manager.start()
    assert sm.current_state == ExperimentState.INITIALIZING
    
    sm.transition_to(ExperimentState.PREPARING)
    sm.transition_to(ExperimentState.TRAINING)
    
    manager.pause()
    assert sm.current_state == ExperimentState.PAUSED
    
    manager.resume()
    assert sm.current_state == ExperimentState.PREPARING
    
    manager.cancel()
    assert sm.current_state == ExperimentState.CANCELLED

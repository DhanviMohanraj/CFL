"""Tests for State Machine.

Author: DriftAdapt Contributors
"""

import pytest
from app.training.state_machine import StateMachine
from app.training.experiment_state import ExperimentState
from app.training.experiment_exceptions import ExperimentError


def test_state_machine_valid_transitions():
    sm = StateMachine()
    assert sm.current_state == ExperimentState.CREATED
    
    sm.transition_to(ExperimentState.INITIALIZING)
    assert sm.current_state == ExperimentState.INITIALIZING
    
    sm.transition_to(ExperimentState.PREPARING)
    assert sm.current_state == ExperimentState.PREPARING

def test_state_machine_invalid_transitions():
    sm = StateMachine()
    
    with pytest.raises(ExperimentError):
        sm.transition_to(ExperimentState.TRAINING)

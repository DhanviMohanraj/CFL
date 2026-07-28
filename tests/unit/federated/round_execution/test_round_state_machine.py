"""Tests for Round State Machine.

Author: DriftAdapt Contributors
"""

import pytest
from app.federated.round_execution.round_state_machine import RoundStateMachine, RoundState
from app.federated.round_execution.execution_exceptions import ExecutionStateError


def test_round_state_machine():
    sm = RoundStateMachine()
    
    assert sm.current_state == RoundState.CREATED
    
    sm.transition_to(RoundState.PREPARING)
    assert sm.current_state == RoundState.PREPARING
    
    sm.transition_to(RoundState.DISPATCHING)
    sm.transition_to(RoundState.TRAINING)
    sm.transition_to(RoundState.COLLECTING)
    sm.transition_to(RoundState.VALIDATING)
    sm.transition_to(RoundState.AGGREGATING)
    sm.transition_to(RoundState.REDISTRIBUTING)
    sm.transition_to(RoundState.COMPLETED)
    
    with pytest.raises(ExecutionStateError):
        sm.transition_to(RoundState.TRAINING)

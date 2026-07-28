"""DriftAdapt Experiment State Machine.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, Set

from app.training.experiment_exceptions import ExperimentError
from app.training.experiment_state import ExperimentState


class StateMachine:
    """Manages valid transitions for experiment states."""
    
    _VALID_TRANSITIONS: Dict[ExperimentState, Set[ExperimentState]] = {
        ExperimentState.CREATED: {ExperimentState.INITIALIZING, ExperimentState.CANCELLED},
        ExperimentState.INITIALIZING: {ExperimentState.PREPARING, ExperimentState.FAILED, ExperimentState.CANCELLED},
        ExperimentState.PREPARING: {ExperimentState.TRAINING, ExperimentState.FAILED, ExperimentState.CANCELLED},
        ExperimentState.TRAINING: {ExperimentState.COMMUNICATING, ExperimentState.PAUSED, ExperimentState.FAILED, ExperimentState.CANCELLED},
        ExperimentState.COMMUNICATING: {ExperimentState.AGGREGATING, ExperimentState.PAUSED, ExperimentState.FAILED, ExperimentState.CANCELLED},
        ExperimentState.AGGREGATING: {ExperimentState.EVALUATING, ExperimentState.PREPARING, ExperimentState.COMPLETED, ExperimentState.FAILED, ExperimentState.CANCELLED},
        ExperimentState.EVALUATING: {ExperimentState.PREPARING, ExperimentState.COMPLETED, ExperimentState.FAILED, ExperimentState.CANCELLED},
        ExperimentState.PAUSED: {ExperimentState.PREPARING, ExperimentState.TRAINING, ExperimentState.COMMUNICATING, ExperimentState.CANCELLED},
        ExperimentState.COMPLETED: set(),
        ExperimentState.CANCELLED: set(),
        ExperimentState.FAILED: set()
    }
    
    def __init__(self, initial_state: ExperimentState = ExperimentState.CREATED) -> None:
        self._current_state = initial_state
        self._lock = threading.RLock()
        
    @property
    def current_state(self) -> ExperimentState:
        with self._lock:
            return self._current_state
            
    def transition_to(self, target_state: ExperimentState) -> None:
        """Transitions to the target state if valid."""
        with self._lock:
            allowed = self._VALID_TRANSITIONS.get(self._current_state, set())
            if target_state not in allowed:
                raise ExperimentError(f"Invalid transition from {self._current_state.value} to {target_state.value}.")
            self._current_state = target_state

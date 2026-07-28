"""DriftAdapt Round State Machine.

Author: DriftAdapt Contributors
"""

from enum import Enum
import threading
from app.federated.round_execution.execution_exceptions import ExecutionStateError


class RoundState(str, Enum):
    """Possible states for round execution."""
    CREATED = "CREATED"
    PREPARING = "PREPARING"
    DISPATCHING = "DISPATCHING"
    TRAINING = "TRAINING"
    COLLECTING = "COLLECTING"
    VALIDATING = "VALIDATING"
    AGGREGATING = "AGGREGATING"
    REDISTRIBUTING = "REDISTRIBUTING"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class RoundStateMachine:
    """Manages the state transitions of a federated round."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._current_state = RoundState.CREATED
        
        self._allowed_transitions = {
            RoundState.CREATED: {RoundState.PREPARING, RoundState.CANCELLED, RoundState.FAILED},
            RoundState.PREPARING: {RoundState.DISPATCHING, RoundState.PAUSED, RoundState.CANCELLED, RoundState.FAILED},
            RoundState.DISPATCHING: {RoundState.TRAINING, RoundState.PAUSED, RoundState.CANCELLED, RoundState.FAILED},
            RoundState.TRAINING: {RoundState.COLLECTING, RoundState.PAUSED, RoundState.CANCELLED, RoundState.FAILED},
            RoundState.COLLECTING: {RoundState.VALIDATING, RoundState.PAUSED, RoundState.CANCELLED, RoundState.FAILED},
            RoundState.VALIDATING: {RoundState.AGGREGATING, RoundState.PAUSED, RoundState.CANCELLED, RoundState.FAILED},
            RoundState.AGGREGATING: {RoundState.REDISTRIBUTING, RoundState.PAUSED, RoundState.CANCELLED, RoundState.FAILED},
            RoundState.REDISTRIBUTING: {RoundState.COMPLETED, RoundState.PAUSED, RoundState.CANCELLED, RoundState.FAILED},
            RoundState.PAUSED: {
                RoundState.PREPARING, RoundState.DISPATCHING, RoundState.TRAINING, 
                RoundState.COLLECTING, RoundState.VALIDATING, RoundState.AGGREGATING, 
                RoundState.REDISTRIBUTING, RoundState.CANCELLED, RoundState.FAILED
            },
            RoundState.COMPLETED: set(),
            RoundState.CANCELLED: set(),
            RoundState.FAILED: set(),
        }
        
    @property
    def current_state(self) -> RoundState:
        with self._lock:
            return self._current_state
            
    def transition_to(self, target_state: RoundState) -> None:
        with self._lock:
            if target_state not in self._allowed_transitions[self._current_state]:
                raise ExecutionStateError(f"Invalid transition from {self._current_state.value} to {target_state.value}.")
            self._current_state = target_state

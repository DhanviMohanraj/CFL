"""DriftAdapt Client Session Tracker.

Author: DriftAdapt Contributors
"""

import time
import uuid
from typing import List, Tuple

from app.federated.client.client_exceptions import RuntimeStateError
from app.federated.client.runtime_state import RuntimeState


class ClientSession:
    """Tracks state and metadata for a single training/communication session."""
    
    def __init__(self, client_id: str, communication_round: int = 1) -> None:
        self.session_id: str = str(uuid.uuid4())
        self.client_id: str = client_id
        self.communication_round: int = communication_round
        self.training_round: int = 0
        self.start_time: float = time.time()
        self.end_time: float = 0.0
        self.failures: int = 0
        self.retries: int = 0
        
        self._current_state: RuntimeState = RuntimeState.IDLE
        self._state_history: List[Tuple[RuntimeState, float]] = [(self._current_state, time.time())]
        
    @property
    def current_state(self) -> RuntimeState:
        return self._current_state
        
    def transition_to(self, new_state: RuntimeState) -> None:
        """Transitions to a new state and logs the transition."""
        # State machine constraints can be added here if needed
        self._current_state = new_state
        self._state_history.append((new_state, time.time()))
        
        if new_state in (RuntimeState.COMPLETED, RuntimeState.FAILED, RuntimeState.STOPPED):
            self.end_time = time.time()
            
    def get_duration(self) -> float:
        """Returns the runtime duration of this session."""
        end = self.end_time if self.end_time > 0 else time.time()
        return end - self.start_time
        
    def increment_failure(self) -> None:
        self.failures += 1
        self.transition_to(RuntimeState.FAILED)

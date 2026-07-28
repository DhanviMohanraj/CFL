"""DriftAdapt Lifecycle Manager.

Author: DriftAdapt Contributors
"""

from app.training.experiment_state import ExperimentState
from app.training.state_machine import StateMachine


class LifecycleManager:
    """Handles startup, shutdown, and interruption of an experiment."""
    
    def __init__(self, state_machine: StateMachine) -> None:
        self._state_machine = state_machine
        
    def start(self) -> None:
        """Triggers the startup sequence."""
        if self._state_machine.current_state == ExperimentState.CREATED:
            self._state_machine.transition_to(ExperimentState.INITIALIZING)
            
    def pause(self) -> None:
        """Pauses the experiment gracefully."""
        self._state_machine.transition_to(ExperimentState.PAUSED)
        
    def resume(self) -> None:
        """Resumes a paused experiment."""
        if self._state_machine.current_state == ExperimentState.PAUSED:
            self._state_machine.transition_to(ExperimentState.PREPARING)
            
    def cancel(self) -> None:
        """Cancels an ongoing experiment."""
        self._state_machine.transition_to(ExperimentState.CANCELLED)
        
    def complete(self) -> None:
        """Marks the experiment as fully completed."""
        self._state_machine.transition_to(ExperimentState.COMPLETED)
        
    def fail(self) -> None:
        """Marks the experiment as failed."""
        self._state_machine.transition_to(ExperimentState.FAILED)

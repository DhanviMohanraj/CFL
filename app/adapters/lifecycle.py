"""DriftAdapt Adapter Version Lifecycle.

Author: DriftAdapt Contributors
Purpose: Manages state transitions for adapter versions.
"""

from enum import Enum

from app.adapters.exceptions import InvalidStateTransition


class VersionState(str, Enum):
    """Enumeration of possible lifecycle states for a version."""
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    ROLLED_BACK = "ROLLED_BACK"
    DELETED = "DELETED"


class VersionLifecycleManager:
    """Validates and applies state transitions for versions."""
    
    # Define valid directed graph transitions
    VALID_TRANSITIONS = {
        VersionState.CREATED: {VersionState.ACTIVE, VersionState.DELETED},
        VersionState.ACTIVE: {VersionState.ARCHIVED, VersionState.ROLLED_BACK, VersionState.DELETED},
        VersionState.ARCHIVED: {VersionState.ACTIVE, VersionState.DELETED},
        VersionState.ROLLED_BACK: {VersionState.ACTIVE, VersionState.ARCHIVED, VersionState.DELETED},
        VersionState.DELETED: set()  # Terminal state
    }
    
    @classmethod
    def transition(cls, current_state: str, new_state: str) -> str:
        """Validates if a transition is legal.
        
        Args:
            current_state: The current state string.
            new_state: The desired target state string.
            
        Returns:
            The validated target state string.
            
        Raises:
            InvalidStateTransition: If the transition is illegal or states are unknown.
        """
        try:
            current = VersionState(current_state)
            target = VersionState(new_state)
        except ValueError:
            raise InvalidStateTransition(f"Unknown state string provided: {current_state} -> {new_state}")
            
        if target not in cls.VALID_TRANSITIONS[current]:
            raise InvalidStateTransition(f"Cannot transition from {current.value} to {target.value}")
            
        return target.value

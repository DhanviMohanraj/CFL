"""DriftAdapt Runtime State Machine.

Author: DriftAdapt Contributors
"""

from enum import Enum


class RuntimeState(Enum):
    """Possible states for the client runtime."""
    IDLE = "IDLE"
    PREPARING = "PREPARING"
    TRAINING = "TRAINING"
    VALIDATING = "VALIDATING"
    PACKAGING = "PACKAGING"
    UPLOADING = "UPLOADING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    STOPPED = "STOPPED"

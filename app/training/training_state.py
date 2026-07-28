"""DriftAdapt Training State.

Author: DriftAdapt Contributors
"""

from enum import Enum


class TrainingState(str, Enum):
    """Possible states for local LoRA training."""
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    PREPARING_DATA = "PREPARING_DATA"
    TRAINING = "TRAINING"
    VALIDATING = "VALIDATING"
    CHECKPOINTING = "CHECKPOINTING"
    EXPORTING = "EXPORTING"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

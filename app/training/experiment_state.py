"""DriftAdapt Experiment State.

Author: DriftAdapt Contributors
"""

from enum import Enum


class ExperimentState(str, Enum):
    """Possible states for a federated experiment."""
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    PREPARING = "PREPARING"
    TRAINING = "TRAINING"
    COMMUNICATING = "COMMUNICATING"
    AGGREGATING = "AGGREGATING"
    EVALUATING = "EVALUATING"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

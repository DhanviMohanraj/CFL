"""DriftAdapt Experiment Exceptions.

Author: DriftAdapt Contributors
"""


class ExperimentError(Exception):
    """Base exception for all experiment errors."""
    pass


class ExperimentInitializationError(ExperimentError):
    """Raised when an experiment fails to initialize."""
    pass


class RoundExecutionError(ExperimentError):
    """Raised when a round execution fails."""
    pass


class DatasetDispatchError(ExperimentError):
    """Raised when dataset dispatching fails."""
    pass


class ClinicUnavailableError(ExperimentError):
    """Raised when a selected clinic is not available."""
    pass


class AggregationDispatchError(ExperimentError):
    """Raised when aggregation trigger fails."""
    pass


class EvaluationDispatchError(ExperimentError):
    """Raised when evaluation trigger fails."""
    pass


class SchedulerError(ExperimentError):
    """Raised when an error occurs during scheduling."""
    pass


class CheckpointRecoveryError(ExperimentError):
    """Raised when checkpoint recovery fails."""
    pass


class ExperimentValidationError(ExperimentError):
    """Raised when an experiment configuration is invalid."""
    pass

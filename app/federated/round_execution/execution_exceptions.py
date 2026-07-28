"""DriftAdapt Execution Exceptions.

Author: DriftAdapt Contributors
"""


class ExecutionError(Exception):
    """Base exception for all federated round execution errors."""
    pass


class RoundInitializationError(ExecutionError):
    """Raised when round initialization fails."""
    pass


class ClientDispatchError(ExecutionError):
    """Raised when dispatching a client fails."""
    pass


class TrainingTimeoutError(ExecutionError):
    """Raised when local training exceeds the maximum allowed time."""
    pass


class AdapterCollectionError(ExecutionError):
    """Raised when adapter collection fails."""
    pass


class AdapterValidationError(ExecutionError):
    """Raised when an collected adapter is invalid."""
    pass


class AggregationTriggerError(ExecutionError):
    """Raised when triggering the aggregation dispatcher fails."""
    pass


class RedistributionError(ExecutionError):
    """Raised when redistributing the global adapter fails."""
    pass


class RoundRecoveryError(ExecutionError):
    """Raised when round recovery from a checkpoint fails."""
    pass


class ExecutionStateError(ExecutionError):
    """Raised when an invalid state transition is attempted."""
    pass

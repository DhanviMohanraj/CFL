"""DriftAdapt Coordinator Exceptions.

Author: DriftAdapt Contributors
"""

class CoordinatorError(Exception):
    """Base exception for all coordinator errors."""
    pass

class RoundInitializationError(CoordinatorError):
    """Raised when a federated round fails to initialize."""
    pass

class ClientSelectionError(CoordinatorError):
    """Raised when the client selection strategy fails."""
    pass

class SynchronizationTimeout(CoordinatorError):
    """Raised when a synchronization barrier times out."""
    pass

class AggregationTriggerError(CoordinatorError):
    """Raised when triggering the aggregation engine fails."""
    pass

class CoordinatorFailure(CoordinatorError):
    """Raised when a catastrophic coordinator failure occurs."""
    pass

class RoundRecoveryError(CoordinatorError):
    """Raised when a round fails to recover from an interrupted state."""
    pass

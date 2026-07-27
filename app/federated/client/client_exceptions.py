"""DriftAdapt Client Runtime Exceptions.

Author: DriftAdapt Contributors
"""


class ClientRuntimeError(Exception):
    """Base exception for client runtime errors."""
    pass


class TrainingSessionError(ClientRuntimeError):
    """Raised when local training fails."""
    pass


class CheckpointError(ClientRuntimeError):
    """Raised when checkpoint saving or loading fails."""
    pass


class ClientRegistrationError(ClientRuntimeError):
    """Raised when client registration with the registry fails."""
    pass


class RuntimeStateError(ClientRuntimeError):
    """Raised when an invalid state transition occurs."""
    pass


class TrainingInterruptedError(ClientRuntimeError):
    """Raised when training is interrupted prematurely."""
    pass

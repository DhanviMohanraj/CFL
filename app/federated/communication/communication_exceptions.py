"""DriftAdapt Communication Exceptions.

Author: DriftAdapt Contributors
Purpose: Custom structured exceptions for federated communication.
"""


class CommunicationError(Exception):
    """Base exception for all communication-related errors."""
    pass


class UploadError(CommunicationError):
    """Raised when an adapter upload fails."""
    pass


class DownloadError(CommunicationError):
    """Raised when an adapter download fails."""
    pass


class SynchronizationError(CommunicationError):
    """Raised when a synchronization round fails."""
    pass


class PackageValidationError(CommunicationError):
    """Raised when an adapter package fails integrity or security validation."""
    pass


class RetryLimitExceeded(CommunicationError):
    """Raised when an operation fails after exhausting all retries."""
    pass


class ProtocolError(CommunicationError):
    """Raised when a transport protocol abstraction fails."""
    pass


class SessionNotFound(CommunicationError):
    """Raised when attempting to interact with a non-existent communication session."""
    pass

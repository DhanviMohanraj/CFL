"""DriftAdapt Runtime Exceptions Module.

Author: DriftAdapt Contributors
Purpose: Defines custom exceptions for environments, hardware selections, and dependency checks.
Future Integration: Raised by RuntimeInitializer and managers during bootstrap.
"""


class RuntimeManagerError(Exception):
    """Base exception for all runtime and resource errors in DriftAdapt."""

    pass


class RuntimeInitializationError(RuntimeManagerError):
    """Raised when the primary system startup sequence fails."""

    pass


class GPUNotAvailableError(RuntimeInitializationError):
    """Raised when preferred hardware (CUDA/MPS) is not accessible on the host."""

    pass


class DependencyMissingError(RuntimeInitializationError):
    """Raised when one or more required Python dependencies are missing from the environment."""

    pass


class InvalidDeviceError(RuntimeInitializationError):
    """Raised when an unrecognized or misconfigured device string is requested."""

    pass


class SeedInitializationError(RuntimeInitializationError):
    """Raised when seed assignment or deterministic configurations fail."""

    pass

"""DriftAdapt Adapter Registry Exceptions Module.

Author: DriftAdapt Contributors
Purpose: Defines custom exceptions for the Federated Adapter Registry.
"""


class AdapterAlreadyExists(Exception):
    """Raised when attempting to register an adapter that already exists."""
    pass


class AdapterNotFound(Exception):
    """Raised when an adapter cannot be found in the registry."""
    pass


class ClinicNotFound(Exception):
    """Raised when no adapters exist for a specified clinic."""
    pass


class InvalidClinicID(Exception):
    """Raised when an invalid clinic ID is provided (e.g., empty string or None)."""
    pass


class RegistryPersistenceError(Exception):
    """Raised when the registry fails to save or load its state."""
    pass

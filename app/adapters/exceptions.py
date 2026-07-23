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


class InvalidAdapterState(Exception):
    """Raised when an adapter state dictionary is invalid."""
    pass


class SerializationError(Exception):
    """Raised when serializing an adapter state fails."""
    pass


class DeserializationError(Exception):
    """Raised when deserializing an adapter state fails."""
    pass


class ChecksumMismatch(Exception):
    """Raised when a computed checksum does not match the expected checksum."""
    pass


class ValidationFailed(Exception):
    """Raised when an adapter state fails strict validation."""
    pass


class UnsupportedFormat(Exception):
    """Raised when an unsupported serialization format is requested."""
    pass

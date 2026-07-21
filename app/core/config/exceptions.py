"""DriftAdapt Configuration Exception Module.

Author: DriftAdapt Contributors
Purpose: Exposes custom exception classes for loading, validation, and override operations.
Future Integration: Raised by loader, validator, and manager components.
"""


class ConfigurationError(Exception):
    """Base exception for all configuration management errors in DriftAdapt."""

    pass


class MissingConfiguration(ConfigurationError):
    """Raised when a required configuration key or section is absent."""

    pass


class ValidationError(ConfigurationError):
    """Raised when configuration values do not match their schema requirements or constraints."""

    pass


class InvalidConfiguration(ConfigurationError):
    """Raised when configuration is syntactically invalid or logically inconsistent."""

    pass


class FileNotFoundConfiguration(ConfigurationError):
    """Raised when a requested configuration file cannot be found on the filesystem."""

    pass

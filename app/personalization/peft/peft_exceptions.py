"""DriftAdapt PEFT Integration Exceptions.

Author: DriftAdapt Contributors
Purpose: Defines custom exceptions for adapter injection and validation errors.
"""


class PEFTIntegrationError(Exception):
    """Base exception for all PEFT integration errors."""
    pass


class AdapterInjectionError(PEFTIntegrationError):
    """Raised when adapter injection fails."""
    pass


class TargetModuleNotFoundError(PEFTIntegrationError):
    """Raised when configured target modules cannot be found in the base model."""
    pass


class AdapterValidationError(PEFTIntegrationError):
    """Raised when an injected adapter fails invariant validation checks."""
    pass


class FrozenModelViolationError(PEFTIntegrationError):
    """Raised when the base model's frozen state is violated during injection."""
    pass

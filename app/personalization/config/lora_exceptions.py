"""DriftAdapt Personalization LoRA Exceptions.

Author: DriftAdapt Contributors
Purpose: Defines domain-specific custom exceptions for LoRA configuration validation and loading.
"""

class LoRAConfigurationError(Exception):
    """Base exception for all LoRA configuration related errors."""
    pass


class ConfigurationNotFoundError(LoRAConfigurationError):
    """Raised when a specified configuration file or resource cannot be found."""
    pass


class ConfigurationValidationError(LoRAConfigurationError):
    """Raised when the parsed configuration violates defined schemas or domain rules."""
    pass


class InvalidRankError(ConfigurationValidationError):
    """Raised when LoRA rank (r) is invalid."""
    pass


class InvalidAlphaError(ConfigurationValidationError):
    """Raised when LoRA alpha is invalid."""
    pass


class InvalidDropoutError(ConfigurationValidationError):
    """Raised when LoRA dropout rate is outside the [0, 1] bounds."""
    pass


class InvalidPrecisionError(ConfigurationValidationError):
    """Raised when the specified precision dtype is not supported."""
    pass


class InvalidTaskTypeError(ConfigurationValidationError):
    """Raised when the PEFT task type is not recognized."""
    pass


class InvalidTargetModuleError(ConfigurationValidationError):
    """Raised when target modules list is empty, contains duplicates, or invalid layer names."""
    pass


class InvalidCheckpointConfigurationError(ConfigurationValidationError):
    """Raised when checkpoint saving rules (like save_every) are invalid."""
    pass


class InvalidStorageConfigurationError(ConfigurationValidationError):
    """Raised when defined storage paths are invalid or cannot be resolved."""
    pass


class InvalidTrainingParameterError(ConfigurationValidationError):
    """Raised when a hyperparameter (e.g. learning rate) has an invalid value."""
    pass

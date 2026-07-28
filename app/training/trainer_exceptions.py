"""DriftAdapt Trainer Exceptions.

Author: DriftAdapt Contributors
"""


class TrainerError(Exception):
    """Base exception for all trainer errors."""
    pass


class TrainerInitializationError(TrainerError):
    """Raised when a local trainer fails to initialize."""
    pass


class DatasetPreparationError(TrainerError):
    """Raised when preparing the monthly dataset fails."""
    pass


class AdapterLoadingError(TrainerError):
    """Raised when loading the LoRA adapter fails."""
    pass


class TrainingExecutionError(TrainerError):
    """Raised when an error occurs during the training loop."""
    pass


class ValidationError(TrainerError):
    """Raised when validation execution fails."""
    pass


class CheckpointError(TrainerError):
    """Raised when checkpoint saving or loading fails."""
    pass


class AdapterExportError(TrainerError):
    """Raised when exporting the updated adapter fails."""
    pass


class TrainerRecoveryError(TrainerError):
    """Raised when recovering a failed trainer state fails."""
    pass


class OptimizerConfigurationError(TrainerError):
    """Raised when an invalid optimizer configuration is provided."""
    pass

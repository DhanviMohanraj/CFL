"""DriftAdapt Core Config Package.

Author: DriftAdapt Contributors
Purpose: Exposes config manager, factories, schemas, and custom exceptions.
Future Integration: Provides configuration parsing and validation across all submodules.
"""

from app.core.config.config_manager import ConfigManager
from app.core.config.config_factory import ConfigFactory
from app.core.config.schema import (
    AppConfig,
    SystemConfig,
    ModelConfig,
    LoRAConfig,
    TrainingConfig,
    FederatedConfig,
    DatasetConfig,
    DriftConfig,
    EvaluationConfig,
    LoggingConfig,
    ExperimentConfig,
)
from app.core.config.exceptions import (
    ConfigurationError,
    MissingConfiguration,
    ValidationError,
    InvalidConfiguration,
    FileNotFoundConfiguration,
)
from app.core.config.loader import get_project_root

__all__ = [
    "ConfigManager",
    "ConfigFactory",
    "AppConfig",
    "SystemConfig",
    "ModelConfig",
    "LoRAConfig",
    "TrainingConfig",
    "FederatedConfig",
    "DatasetConfig",
    "DriftConfig",
    "EvaluationConfig",
    "LoggingConfig",
    "ExperimentConfig",
    "ConfigurationError",
    "MissingConfiguration",
    "ValidationError",
    "InvalidConfiguration",
    "FileNotFoundConfiguration",
    "get_project_root",
]

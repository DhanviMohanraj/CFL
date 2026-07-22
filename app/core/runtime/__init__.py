"""DriftAdapt Runtime Package.

Author: DriftAdapt Contributors
Purpose: Exposes RuntimeManager, EnvironmentManager, DependencyChecker, and custom exceptions.
Future Integration: Referenced by all start scripts and system modules.
"""

from app.core.runtime.dependency_checker import DependencyChecker
from app.core.runtime.environment import EnvironmentManager
from app.core.runtime.exceptions import (
    DependencyMissingError,
    GPUNotAvailableError,
    InvalidDeviceError,
    RuntimeInitializationError,
    RuntimeManagerError,
    SeedInitializationError,
)
from app.core.runtime.runtime_info import RuntimeInfo
from app.core.runtime.runtime_manager import RuntimeManager
from app.core.runtime.startup import RuntimeInitializer

__all__ = [
    "RuntimeManagerError",
    "RuntimeInitializationError",
    "GPUNotAvailableError",
    "DependencyMissingError",
    "InvalidDeviceError",
    "SeedInitializationError",
    "EnvironmentManager",
    "DependencyChecker",
    "RuntimeInfo",
    "RuntimeInitializer",
    "RuntimeManager",
]

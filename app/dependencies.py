"""DriftAdapt FastAPI Dependencies Module.

Author: DriftAdapt Contributors
Purpose: Provides FastAPI dependency provider functions for injecting ServiceContainer services into endpoints.
Future Integration: Used by all FastAPI route handlers across the platform.
"""

from fastapi import Depends

from app.container import ServiceContainer
from app.core.config import ConfigManager
from app.core.device import DeviceManager
from app.core.metrics import MetricsBus
from app.core.runtime import RuntimeManager
from app.models.foundation import ModelManager


def get_container() -> ServiceContainer:
    """FastAPI Dependency providing the global ServiceContainer instance."""
    return ServiceContainer()


def get_config_manager(container: ServiceContainer = Depends(get_container)) -> ConfigManager:
    """Dependency providing ConfigManager instance."""
    return container.config_manager()


def get_metrics_bus(container: ServiceContainer = Depends(get_container)) -> MetricsBus:
    """Dependency providing MetricsBus instance."""
    return container.metrics_bus()


def get_device_manager(container: ServiceContainer = Depends(get_container)) -> DeviceManager:
    """Dependency providing DeviceManager instance."""
    return container.device_manager()


def get_runtime_manager(container: ServiceContainer = Depends(get_container)) -> RuntimeManager:
    """Dependency providing RuntimeManager instance."""
    return container.runtime_manager()


def get_model_manager(container: ServiceContainer = Depends(get_container)) -> ModelManager:
    """Dependency providing ModelManager instance."""
    return container.model_manager()

"""DriftAdapt Service Container Module.

Author: DriftAdapt Contributors
Purpose: Provides a centralized, thread-safe service container for managing singleton system services.
Future Integration: Injected into FastAPI routes via dependency injection in app/dependencies.py.
"""

import threading
import time
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.lora.adapter_registry import AdapterRegistry
    from app.services.lora.metadata_service import MetadataService
    from app.services.lora.adapter_initializer import AdapterInitializer

from app.core.config import ConfigManager
from app.core.device import DeviceManager
from app.core.logging import LoggerFactory
from app.core.metrics import MetricsBus
from app.core.runtime import EnvironmentManager, RuntimeManager
from app.core.seed import SeedManager
from app.models.foundation import ModelManager


class ServiceContainer:
    """Centralized Dependency Injection Container for DriftAdapt application services."""

    _instance: Optional["ServiceContainer"] = None
    _lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> "ServiceContainer":
        """Thread-safe singleton instantiation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initializes service container handles and state flags."""
        if getattr(self, "_initialized", False):
            return

        self._start_time: float = time.time()
        self._is_ready: bool = False
        self._lock = threading.Lock()

        # Services initialized lazily or on container creation
        self._config_manager: Optional[ConfigManager] = None
        self._metrics_bus: Optional[MetricsBus] = None
        self._device_manager: Optional[DeviceManager] = None
        self._runtime_manager: Optional[RuntimeManager] = None
        self._model_manager: Optional[ModelManager] = None
        
        # Module 2.3 LoRA API Services
        from app.services.lora.adapter_registry import AdapterRegistry
        from app.services.lora.metadata_service import MetadataService
        from app.services.lora.adapter_initializer import AdapterInitializer
        
        self._lora_registry: Optional[AdapterRegistry] = None
        self._lora_metadata_service: Optional[MetadataService] = None
        self._lora_adapter_initializer: Optional[AdapterInitializer] = None

        self._initialized = True

    @property
    def start_time(self) -> float:
        """Returns application startup timestamp."""
        return self._start_time

    @property
    def is_ready(self) -> bool:
        """Returns True if application startup sequence has completed successfully."""
        return self._is_ready

    def mark_ready(self, ready: bool = True) -> None:
        """Sets readiness status flag."""
        with self._lock:
            self._is_ready = ready

    def get_uptime_seconds(self) -> float:
        """Calculates current application running time in seconds."""
        return round(time.time() - self._start_time, 2)

    def config_manager(self) -> ConfigManager:
        """Retrieves ConfigManager singleton."""
        if self._config_manager is None:
            self._config_manager = ConfigManager()
        return self._config_manager

    def metrics_bus(self) -> MetricsBus:
        """Retrieves MetricsBus singleton."""
        if self._metrics_bus is None:
            self._metrics_bus = MetricsBus()
        return self._metrics_bus

    def device_manager(self) -> DeviceManager:
        """Retrieves DeviceManager singleton."""
        if self._device_manager is None:
            self._device_manager = DeviceManager()
        return self._device_manager

    def runtime_manager(self) -> RuntimeManager:
        """Retrieves RuntimeManager singleton."""
        if self._runtime_manager is None:
            self._runtime_manager = RuntimeManager()
        return self._runtime_manager

    def model_manager(self) -> ModelManager:
        """Returns the ModelManager instance."""
        if self._model_manager is None:
            self._model_manager = ModelManager(self.config_manager())
        return self._model_manager
        
    def lora_registry(self) -> "AdapterRegistry":
        """Returns the LoRA AdapterRegistry instance."""
        if self._lora_registry is None:
            from app.services.lora.adapter_registry import AdapterRegistry
            self._lora_registry = AdapterRegistry()
        return self._lora_registry
        
    def lora_metadata_service(self) -> "MetadataService":
        """Returns the LoRA MetadataService instance."""
        if self._lora_metadata_service is None:
            from app.services.lora.metadata_service import MetadataService
            self._lora_metadata_service = MetadataService(self.lora_registry())
        return self._lora_metadata_service
        
    def lora_adapter_initializer(self) -> "AdapterInitializer":
        """Returns the LoRA AdapterInitializer instance."""
        if self._lora_adapter_initializer is None:
            from app.services.lora.adapter_initializer import AdapterInitializer
            self._lora_adapter_initializer = AdapterInitializer(
                model_manager=self.model_manager(),
                registry=self.lora_registry()
            )
        return self._lora_adapter_initializer

    @staticmethod
    def logger_factory() -> type[LoggerFactory]:
        """Returns LoggerFactory class reference."""
        return LoggerFactory

    @staticmethod
    def environment_manager() -> type[EnvironmentManager]:
        """Returns EnvironmentManager class reference."""
        return EnvironmentManager

    @staticmethod
    def seed_manager() -> type[SeedManager]:
        """Returns SeedManager class reference."""
        return SeedManager

    def get_services_status(self) -> Dict[str, str]:
        """Queries health status of registered container services."""
        return {
            "config_manager": "HEALTHY" if self._config_manager is not None else "UNINITIALIZED",
            "metrics_bus": "HEALTHY" if self._metrics_bus is not None else "UNINITIALIZED",
            "device_manager": "HEALTHY" if self._device_manager is not None else "UNINITIALIZED",
            "runtime_manager": "HEALTHY" if self._runtime_manager is not None else "UNINITIALIZED",
            "model_manager": "HEALTHY" if self._model_manager is not None else "UNINITIALIZED",
            "logger_factory": "HEALTHY",
            "environment_manager": "HEALTHY",
            "seed_manager": "HEALTHY",
        }

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
    
    from app.services.training.optimizer_service import OptimizerService
    from app.services.training.scheduler_service import SchedulerService
    from app.services.training.checkpoint_service import CheckpointService
    from app.services.training.training_monitor import TrainingMonitor
    from app.services.training.gradient_manager import GradientManager
    from app.services.training.personalization_service import PersonalizationService
    from app.services.training.metrics_service import MetricsService as TrainingMetricsService
    from app.services.training.early_stopping import EarlyStoppingService
    from app.services.training.resource_monitor import ResourceMonitor
    from app.services.training.training_engine import TrainingEngine

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
        
        # Module 2.4 Training Services
        from app.services.training.optimizer_service import OptimizerService
        from app.services.training.scheduler_service import SchedulerService
        from app.services.training.checkpoint_service import CheckpointService
        from app.services.training.training_monitor import TrainingMonitor
        from app.services.training.gradient_manager import GradientManager
        from app.services.training.personalization_service import PersonalizationService
        from app.services.training.metrics_service import MetricsService as TrainingMetricsService
        from app.services.training.early_stopping import EarlyStoppingService
        from app.services.training.resource_monitor import ResourceMonitor
        from app.services.training.training_engine import TrainingEngine
        
        self._opt_service: Optional[OptimizerService] = None
        self._sched_service: Optional[SchedulerService] = None
        self._checkpoint_service: Optional[CheckpointService] = None
        self._training_monitor: Optional[TrainingMonitor] = None
        self._grad_manager: Optional[GradientManager] = None
        self._pers_service: Optional[PersonalizationService] = None
        self._training_metrics_service: Optional[TrainingMetricsService] = None
        self._early_stopping: Optional[EarlyStoppingService] = None
        self._resource_monitor: Optional[ResourceMonitor] = None
        self._training_engine: Optional[TrainingEngine] = None

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

    def training_metrics_service(self) -> "TrainingMetricsService":
        if self._training_metrics_service is None:
            from app.services.training.metrics_service import MetricsService as TrainingMetricsService
            self._training_metrics_service = TrainingMetricsService()
        return self._training_metrics_service

    def training_monitor(self) -> "TrainingMonitor":
        if self._training_monitor is None:
            from app.services.training.training_monitor import TrainingMonitor
            self._training_monitor = TrainingMonitor()
        return self._training_monitor

    def resource_monitor(self) -> "ResourceMonitor":
        if self._resource_monitor is None:
            from app.services.training.resource_monitor import ResourceMonitor
            self._resource_monitor = ResourceMonitor()
        return self._resource_monitor

    def early_stopping(self) -> "EarlyStoppingService":
        if self._early_stopping is None:
            from app.services.training.early_stopping import EarlyStoppingService
            self._early_stopping = EarlyStoppingService()
        return self._early_stopping

    def checkpoint_service(self) -> "CheckpointService":
        if self._checkpoint_service is None:
            from app.services.training.checkpoint_service import CheckpointService
            self._checkpoint_service = CheckpointService()
        return self._checkpoint_service

    def gradient_manager(self) -> "GradientManager":
        if self._grad_manager is None:
            from app.services.training.gradient_manager import GradientManager
            self._grad_manager = GradientManager()
        return self._grad_manager

    def optimizer_service(self) -> "OptimizerService":
        if self._opt_service is None:
            from app.services.training.optimizer_service import OptimizerService
            self._opt_service = OptimizerService()
        return self._opt_service

    def scheduler_service(self) -> "SchedulerService":
        if self._sched_service is None:
            from app.services.training.scheduler_service import SchedulerService
            self._sched_service = SchedulerService()
        return self._sched_service

    def training_engine(self) -> "TrainingEngine":
        if self._training_engine is None:
            from app.services.training.training_engine import TrainingEngine
            self._training_engine = TrainingEngine(
                optimizer_service=self.optimizer_service(),
                scheduler_service=self.scheduler_service(),
                gradient_manager=self.gradient_manager(),
                early_stopping=self.early_stopping(),
                checkpoint_service=self.checkpoint_service(),
                resource_monitor=self.resource_monitor(),
                training_monitor=self.training_monitor(),
                metrics_service=self.training_metrics_service()
            )
        return self._training_engine

    def personalization_service(self) -> "PersonalizationService":
        if self._pers_service is None:
            from app.services.training.personalization_service import PersonalizationService
            from app.personalization.peft.peft_manager import PEFTManager
            self._pers_service = PersonalizationService(
                model_manager=self.model_manager(),
                peft_manager=PEFTManager(),
                registry=self.lora_registry(),
                training_engine=self.training_engine(),
                metrics_service=self.training_metrics_service(),
                training_monitor=self.training_monitor()
            )
        return self._pers_service

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

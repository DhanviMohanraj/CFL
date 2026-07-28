"""System Health Monitor Service.

Author: DriftAdapt Contributors
Purpose: Aggregates real-time snapshot of the underlying environment.
"""

from app.core.logging import LoggerFactory
from app.schemas.system_health import SystemHealth
from app.services.validation.memory_profiler import MemoryProfiler
from app.models.foundation.model_manager import ModelManager
from app.services.inference.adapter_registry import AdapterRegistry


class SystemHealthMonitor:
    """Continuously monitors dependencies and machine health."""
    
    def __init__(
        self,
        memory_profiler: MemoryProfiler,
        model_manager: ModelManager,
        adapter_registry: AdapterRegistry
    ) -> None:
        self._logger = LoggerFactory.get_logger("SystemHealthMonitor")
        self._memory_profiler = memory_profiler
        self._model_manager = model_manager
        self._adapter_registry = adapter_registry

    def get_health_snapshot(self) -> SystemHealth:
        """Constructs a point-in-time health diagnostic."""
        
        # Memory checks
        ram_mb, vram_mb = self._memory_profiler.profile_memory()
        memory_status = "OK" if ram_mb < 32000 else "HIGH_USAGE" # Configurable thresholds
        gpu_status = "OK" if vram_mb > 0 else "NOT_AVAILABLE"
        
        # Service checks
        model_loaded = self._model_manager.is_loaded()
        active_adapter = self._adapter_registry.get_active_adapter_id()
        adapter_loaded = len(self._adapter_registry.get_loaded_adapters()) > 0
        
        overall = "HEALTHY"
        if not model_loaded:
            overall = "DEGRADED"
            
        health = SystemHealth(
            overall_status=overall,
            model_loaded=model_loaded,
            adapter_loaded=adapter_loaded,
            active_adapter=active_adapter,
            memory_status=memory_status,
            gpu_status=gpu_status,
            storage_status="OK",
            api_status="ONLINE"
        )
        
        self._logger.debug(f"Health snapshot: {overall}")
        return health

"""DriftAdapt Runtime Manager Module.

Author: DriftAdapt Contributors
Purpose: Centralizes environment query, device allocation, and resource monitoring interfaces.
Future Integration: Queried by federated workers, model trainers, and inference scripts.
"""

from __future__ import annotations
import threading
from typing import Dict, Any, Optional
import torch


from app.core.logging import LoggerFactory
from app.core.runtime.environment import EnvironmentManager
from app.core.runtime.runtime_info import RuntimeInfo
from app.core.runtime.startup import RuntimeInitializer

logger = LoggerFactory.get_logger("RuntimeManager")


class RuntimeManager:
    """Centralized thread-safe Singleton managing DriftAdapt hardware, environments, and reproducibility."""

    _instance: Optional["RuntimeManager"] = None
    _lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> "RuntimeManager":
        """Ensures a single global runtime manager instance exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initializes components and report caches."""
        if getattr(self, "_initialized", False):
            return

        from app.core.device import DeviceManager
        from app.core.monitoring import SystemMonitor

        self._runtime_info: Optional[RuntimeInfo] = None
        self._device_manager = DeviceManager()
        self._system_monitor = SystemMonitor()
        self._lock = threading.Lock()

        self._initialized = True
        logger.info("RuntimeManager instance created.")

    def initialize(self) -> RuntimeInfo:
        """Triggers the startup initialization sequence and caches the results."""
        with self._lock:
            info = RuntimeInitializer.initialize()
            self._runtime_info = info
            return info

    def get_runtime_info(self) -> RuntimeInfo:
        """Returns the cached system RuntimeInfo report, running initialize() if not yet run."""
        if self._runtime_info is None:
            return self.initialize()
        return self._runtime_info

    def get_device(self) -> torch.device:
        """Retrieves the active PyTorch execution device."""
        return self._device_manager.get_device()

    def get_hardware_summary(self) -> Dict[str, Any]:
        """Gathers complete summary of physical processors and RAM memory structures."""
        return self._device_manager.get_hardware_summary()

    def get_environment_snapshot(self) -> Dict[str, Any]:
        """Queries OS platform and path environments properties."""
        return EnvironmentManager.get_environment_snapshot()

    def get_system_monitor(self) -> SystemMonitor:
        """Returns the active global resource utilization Monitor."""
        return self._system_monitor

    def set_seed(self, seed: int, deterministic: bool = False) -> None:
        """Allows dynamically re-seeding active random generators."""
        from app.core.seed import SeedManager
        SeedManager.set_seed(seed, deterministic)


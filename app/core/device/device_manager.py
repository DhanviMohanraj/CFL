"""DriftAdapt Device Manager Module.

Author: DriftAdapt Contributors
Purpose: Centralizes hardware query details and manages active device selections.
Future Integration: Invoked by model loaders and training nodes to target computation hardware.
"""

import threading
from typing import Dict, Any, List, Optional
import torch

from app.core.device.cpu_manager import CPUManager
from app.core.device.gpu_manager import GPUManager
from app.core.device.memory_manager import MemoryManager
from app.core.device.device_factory import DeviceFactory
from app.core.device.device_info import CPUInfo, GPUInfo, MemoryInfo
from app.core.logging import LoggerFactory
from app.core.runtime.exceptions import InvalidDeviceError

logger = LoggerFactory.get_logger("DeviceManager")


class DeviceManager:
    """Singleton orchestrator to resolve physical hardware specs and allocate PyTorch execution devices."""

    _instance: Optional["DeviceManager"] = None
    _lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> "DeviceManager":
        """Ensures single global instance is cached and thread-safe."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initializes device properties cache."""
        if getattr(self, "_initialized", False):
            return

        self._cpu_info: Optional[CPUInfo] = None
        self._gpus_info: Optional[List[GPUInfo]] = None
        self._memory_info: Optional[MemoryInfo] = None
        self._active_device: Optional[torch.device] = None

        self._initialized = True
        logger.info("DeviceManager initialized successfully.")

    def get_cpu_info(self, force_refresh: bool = False) -> CPUInfo:
        """Retrieves cached CPU specs, refreshing if requested."""
        if self._cpu_info is None or force_refresh:
            self._cpu_info = CPUManager.get_cpu_info()
        return self._cpu_info

    def get_gpus_info(self, force_refresh: bool = False) -> List[GPUInfo]:
        """Retrieves cached GPU specs list, refreshing if requested."""
        if self._gpus_info is None or force_refresh:
            self._gpus_info = GPUManager.get_gpus_info()
        return self._gpus_info

    def get_memory_info(self, force_refresh: bool = False) -> MemoryInfo:
        """Retrieves cached RAM/Swap allocations, refreshing if requested."""
        if self._memory_info is None or force_refresh:
            self._memory_info = MemoryManager.get_memory_info()
        return self._memory_info

    def get_best_device(self) -> torch.device:
        """Auto-selects the best hardware device available on the host platform.

        Hierarchy: CUDA -> MPS -> CPU
        """
        # 1. CUDA
        if GPUManager.is_cuda_available():
            logger.info("Automatically selected CUDA device as the best available target.")
            return torch.device("cuda")

        # 2. MPS
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            logger.info("Automatically selected Apple Silicon MPS device as the best available target.")
            return torch.device("mps")

        # 3. CPU fallback
        logger.info("Automatically selected CPU fallback device.")
        return torch.device("cpu")

    def resolve_device(self, preferred_device_str: Optional[str] = None) -> torch.device:
        """Parses and yields the active device, falling back to auto-selection if needed."""
        if self._active_device is not None and preferred_device_str is None:
            return self._active_device

        device_str = preferred_device_str or "auto"
        logger.info(f"Resolving device target for value: '{device_str}'")

        if device_str.lower().strip() == "auto":
            self._active_device = self.get_best_device()
            return self._active_device

        try:
            # Attempt to allocate via factory
            self._active_device = DeviceFactory.create_device(device_str)
            logger.info(f"Target device successfully set to preferred configuration: {self._active_device}")
        except InvalidDeviceError as ide:
            # Fall back to best available rather than crashing, log warning
            logger.warning(
                f"Preferred device '{device_str}' failed validation: {ide}. "
                "Automatically falling back to best available hardware."
            )
            self._active_device = self.get_best_device()

        return self._active_device

    def get_device(self) -> torch.device:
        """Returns the current active device. Allocates auto if none resolved yet."""
        if self._active_device is None:
            self._active_device = self.get_best_device()
        return self._active_device

    def get_hardware_summary(self) -> Dict[str, Any]:
        """Compiles a complete structured description of system hardware configurations."""
        cpu = self.get_cpu_info(force_refresh=True)
        gpus = self.get_gpus_info(force_refresh=True)
        mem = self.get_memory_info(force_refresh=True)

        return {
            "device": str(self.get_device()),
            "cpu": cpu.model_dump(),
            "gpu_count": len(gpus),
            "gpus": [g.model_dump() for g in gpus],
            "memory": mem.model_dump(),
        }

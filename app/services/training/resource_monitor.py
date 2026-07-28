"""DriftAdapt Resource Monitor Service.

Author: DriftAdapt Contributors
Purpose: Tracks CPU, GPU, and RAM utilization during training and raises limits.
"""

import psutil
from typing import Dict, Any

try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

from app.core.logging import LoggerFactory


class ResourceMonitor:
    """Service to track hardware telemetry and enforce safe bounds."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("ResourceMonitor")
        global NVML_AVAILABLE
        if NVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
            except pynvml.NVMLError:
                self._logger.warning("NVML library found but initialization failed.")
                NVML_AVAILABLE = False

    def get_resource_usage(self) -> Dict[str, Any]:
        """Polls current hardware utilization metrics.

        Returns:
            Dictionary containing CPU percentage, RAM mb, and GPU details.
        """
        mem = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=None)

        usage = {
            "cpu_percent": cpu_percent,
            "ram_used_mb": mem.used / (1024 * 1024),
            "ram_total_mb": mem.total / (1024 * 1024),
            "gpu_percent": 0.0,
            "gpu_memory_used_mb": 0.0
        }

        if NVML_AVAILABLE:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                usage["gpu_memory_used_mb"] = gpu_mem.used / (1024 * 1024)

                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                usage["gpu_percent"] = util.gpu
            except pynvml.NVMLError:
                pass

        return usage

    def check_limits(self, max_ram_percent: float = 95.0, max_gpu_percent: float = 95.0) -> bool:
        """Checks if hardware utilization exceeds safety thresholds.

        Args:
            max_ram_percent: Maximum acceptable system RAM %.
            max_gpu_percent: Maximum acceptable GPU Memory %.

        Returns:
            False if limits are exceeded, True otherwise.
        """
        mem = psutil.virtual_memory()
        if mem.percent > max_ram_percent:
            self._logger.warning(f"CRITICAL: System RAM utilization at {mem.percent}%")
            return False

        if NVML_AVAILABLE:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_percent = (gpu_mem.used / gpu_mem.total) * 100.0
                if gpu_percent > max_gpu_percent:
                    self._logger.warning(f"CRITICAL: GPU VRAM utilization at {gpu_percent}%")
                    return False
            except pynvml.NVMLError:
                pass

        return True

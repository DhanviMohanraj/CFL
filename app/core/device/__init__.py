"""DriftAdapt Device Package.

Author: DriftAdapt Contributors
Purpose: Exposes CPU, GPU, Memory managers, DeviceFactory, and DeviceManager interfaces.
Future Integration: Referenced by platform loaders and validation suites.
"""

from app.core.device.cpu_manager import CPUManager
from app.core.device.device_factory import DeviceFactory
from app.core.device.device_info import CPUInfo, GPUInfo, MemoryInfo
from app.core.device.device_manager import DeviceManager
from app.core.device.gpu_manager import GPUManager
from app.core.device.memory_manager import MemoryManager

__all__ = [
    "CPUInfo",
    "GPUInfo",
    "MemoryInfo",
    "CPUManager",
    "GPUManager",
    "MemoryManager",
    "DeviceFactory",
    "DeviceManager",
]

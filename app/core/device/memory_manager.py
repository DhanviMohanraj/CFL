"""DriftAdapt Memory Manager Module.

Author: DriftAdapt Contributors
Purpose: Detects RAM and swap capacities, allocations, and states.
Future Integration: Invoked by DeviceManager and MemoryMonitor.
"""

from app.core.device.device_info import MemoryInfo

try:
    import psutil
except ImportError:
    psutil = None


class MemoryManager:
    """Manages system memory detection (RAM, Virtual, and Swap spaces)."""

    @classmethod
    def get_memory_info(cls) -> MemoryInfo:
        """Gathers and returns detailed MemoryInfo. Values in Gigabytes (GB)."""
        total_ram = 0.0
        avail_ram = 0.0
        used_ram = 0.0
        total_swap = 0.0
        avail_swap = 0.0

        if psutil is not None:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            total_ram = mem.total / (1024**3)
            avail_ram = mem.available / (1024**3)
            used_ram = mem.used / (1024**3)

            total_swap = swap.total / (1024**3)
            avail_swap = swap.free / (1024**3)
        else:
            # Fallback values
            total_ram = 8.0
            avail_ram = 4.0
            used_ram = 4.0

        return MemoryInfo(
            total_ram_gb=round(total_ram, 2),
            available_ram_gb=round(avail_ram, 2),
            used_ram_gb=round(used_ram, 2),
            total_swap_gb=round(total_swap, 2),
            available_swap_gb=round(avail_swap, 2),
        )

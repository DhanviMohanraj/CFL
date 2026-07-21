"""DriftAdapt Memory Monitor Module.

Author: DriftAdapt Contributors
Purpose: Exposes RAM memory and Swap space allocation polling.
Future Integration: Invoked by SystemMonitor.
"""

from typing import Dict, Any
from app.core.device.memory_manager import MemoryManager


class MemoryMonitor:
    """Monitors physical RAM memory and Swap partitions utilization."""

    @staticmethod
    def get_snapshot() -> Dict[str, Any]:
        """Collects current physical RAM and Swap allocations. Values in GB."""
        mem_info = MemoryManager.get_memory_info()

        # Calculate percentage used
        ram_percent = 0.0
        if mem_info.total_ram_gb > 0:
            ram_percent = (mem_info.used_ram_gb / mem_info.total_ram_gb) * 100

        swap_percent = 0.0
        used_swap = mem_info.total_swap_gb - mem_info.available_swap_gb
        if mem_info.total_swap_gb > 0:
            swap_percent = (used_swap / mem_info.total_swap_gb) * 100

        return {
            "total_ram_gb": mem_info.total_ram_gb,
            "available_ram_gb": mem_info.available_ram_gb,
            "used_ram_gb": mem_info.used_ram_gb,
            "ram_utilization_percent": round(ram_percent, 2),
            "total_swap_gb": mem_info.total_swap_gb,
            "used_swap_gb": round(used_swap, 2),
            "swap_utilization_percent": round(swap_percent, 2),
        }

"""DriftAdapt GPU Monitor Module.

Author: DriftAdapt Contributors
Purpose: Exposes GPU graphics processor memory, load, and availability polling.
Future Integration: Invoked by SystemMonitor.
"""

from typing import Dict, Any, List
from app.core.device.gpu_manager import GPUManager

try:
    import torch
except ImportError:
    torch = None


class GPUMonitor:
    """Monitors GPU memory allocation, usage, and availability stats."""

    @staticmethod
    def get_snapshot() -> Dict[str, Any]:
        """Collects current GPU performance, memory stats, and availability."""
        cuda_avail = GPUManager.is_cuda_available()
        gpus = GPUManager.get_gpus_info()

        gpu_snaps: List[Dict[str, Any]] = []
        for g in gpus:
            gpu_snaps.append(
                {
                    "index": g.index,
                    "name": g.name,
                    "allocated_memory_mb": round(g.total_memory_mb - g.available_memory_mb, 2),
                    "available_memory_mb": g.available_memory_mb,
                    "total_memory_mb": g.total_memory_mb,
                    "utilization_percent": 0.0,  # placeholder or NVML query
                }
            )

        # Calculate averages for system report
        total_allocated = sum(g["allocated_memory_mb"] for g in gpu_snaps)
        total_mem = sum(g["total_memory_mb"] for g in gpu_snaps)

        return {
            "cuda_available": cuda_avail,
            "device_count": len(gpus),
            "allocated_memory_mb": total_allocated,
            "total_memory_mb": total_mem,
            "gpus": gpu_snaps,
        }

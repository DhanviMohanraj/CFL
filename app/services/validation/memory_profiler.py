"""Memory Profiler Service.

Author: DriftAdapt Contributors
Purpose: Captures host RAM and VRAM allocation statistics.
"""

import psutil
from typing import Tuple

try:
    import torch
except ImportError:
    pass

from app.core.logging import LoggerFactory


class MemoryProfiler:
    """Profiles and records system memory usage during benchmarking."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("MemoryProfiler")

    def profile_memory(self) -> Tuple[float, float]:
        """Snapshots current memory utilization.
        
        Returns:
            Tuple of (ram_usage_mb, vram_usage_mb)
        """
        try:
            process = psutil.Process()
            ram_usage_mb = process.memory_info().rss / (1024 * 1024)
            
            vram_usage_mb = 0.0
            if torch.cuda.is_available():
                # We record max allocated for a high-water mark, or just current allocated
                vram_usage_mb = torch.cuda.memory_allocated() / (1024 * 1024)
                
            return ram_usage_mb, vram_usage_mb
            
        except Exception as e:
            self._logger.error("Failed to profile memory", error=str(e))
            return 0.0, 0.0

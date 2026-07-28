"""Adapter Benchmark Service.

Author: DriftAdapt Contributors
Purpose: Profiles I/O and injection speeds for PEFT adapters.
"""

import time
from typing import Optional

from app.core.logging import LoggerFactory
from app.services.inference.adapter_loader import AdapterLoader
from app.services.inference.adapter_switcher import AdapterSwitcher


class AdapterBenchmark:
    """Measures the overhead of loading and swapping adapters."""
    
    def __init__(self, adapter_loader: AdapterLoader, adapter_switcher: AdapterSwitcher) -> None:
        self._logger = LoggerFactory.get_logger("AdapterBenchmark")
        self._adapter_loader = adapter_loader
        self._adapter_switcher = adapter_switcher

    def run_loading_benchmark(self, adapter_id: str, adapter_path: str) -> float:
        """Benchmarks a cold load of an adapter from disk.
        
        Returns:
            Load time in seconds.
        """
        # Ensure unloaded first
        self._adapter_loader.unload_adapter(adapter_id)
        
        start_time = time.perf_counter()
        success = self._adapter_loader.load_adapter(adapter_id, adapter_path)
        elapsed = time.perf_counter() - start_time
        
        if success:
            self._logger.info(f"Adapter cold-load benchmark: {elapsed:.4f}s")
            return elapsed
        return 0.0

    def run_switching_benchmark(self, adapter_id: str) -> float:
        """Benchmarks switching active adapters in VRAM.
        
        Returns:
            Switch time in seconds.
        """
        # Switch to None first
        self._adapter_switcher.switch_adapter(None)
        
        start_time = time.perf_counter()
        success = self._adapter_switcher.switch_adapter(adapter_id)
        elapsed = time.perf_counter() - start_time
        
        if success:
            self._logger.info(f"Adapter VRAM switch benchmark: {elapsed:.4f}s")
            return elapsed
        return 0.0

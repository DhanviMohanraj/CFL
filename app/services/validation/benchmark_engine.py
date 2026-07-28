"""Benchmark Engine Service.

Author: DriftAdapt Contributors
Purpose: Orchestrates the execution of latency, throughput, and memory profiling benchmark suites.
"""

import time
from typing import Optional

from app.core.logging import LoggerFactory
from app.schemas.benchmark_request import BenchmarkRequest
from app.schemas.benchmark_result import BenchmarkResult
from app.services.validation.latency_benchmark import LatencyBenchmark
from app.services.validation.throughput_benchmark import ThroughputBenchmark
from app.services.validation.memory_profiler import MemoryProfiler
from app.services.validation.adapter_benchmark import AdapterBenchmark
from app.services.validation.metrics_collector import MetricsCollector
from app.services.validation.validation_history import ValidationHistory
from app.services.validation.validation_registry import ValidationRegistry


class BenchmarkEngine:
    """Coordinates multi-modal performance evaluations."""
    
    def __init__(
        self,
        latency_bm: LatencyBenchmark,
        throughput_bm: ThroughputBenchmark,
        memory_profiler: MemoryProfiler,
        adapter_bm: AdapterBenchmark,
        metrics_collector: MetricsCollector,
        history: ValidationHistory,
        registry: ValidationRegistry
    ) -> None:
        self._logger = LoggerFactory.get_logger("BenchmarkEngine")
        self._latency = latency_bm
        self._throughput = throughput_bm
        self._memory = memory_profiler
        self._adapter_bm = adapter_bm
        self._metrics = metrics_collector
        self._history = history
        self._registry = registry

    def run_benchmark(self, request: BenchmarkRequest) -> BenchmarkResult:
        """Executes the requested benchmarking suite."""
        if self._registry.is_benchmark_running():
            raise RuntimeError("Another benchmark is currently running.")
            
        self._registry.register_benchmark(request.benchmark_id)
        start_time = time.perf_counter()
        
        try:
            self._logger.info(f"Starting benchmark {request.benchmark_id} of type {request.benchmark_type}")
            
            avg_lat, min_lat, max_lat = 0.0, 0.0, 0.0
            throughput = 0.0
            
            # Record base memory
            ram_mb_start, vram_mb_start = self._memory.profile_memory()
            
            if request.benchmark_type in ["latency", "all"]:
                avg_lat, min_lat, max_lat = self._latency.run_latency_test(
                    request.iterations, request.warmup_runs, request.adapter_id
                )
                
            if request.benchmark_type in ["throughput", "all"]:
                throughput = self._throughput.run_throughput_test(
                    request.iterations, request.adapter_id
                )
                
            # Record peak memory roughly after load
            ram_mb_end, vram_mb_end = self._memory.profile_memory()
            peak_ram = max(ram_mb_start, ram_mb_end)
            peak_vram = max(vram_mb_start, vram_mb_end)
            
            elapsed = time.perf_counter() - start_time
            
            result = BenchmarkResult(
                benchmark_id=request.benchmark_id,
                benchmark_type=request.benchmark_type,
                average_latency=avg_lat,
                minimum_latency=min_lat,
                maximum_latency=max_lat,
                throughput=throughput,
                memory_usage=peak_ram,
                gpu_usage=peak_vram,
                cpu_usage=0.0, # Would require a background thread profiling psutil over the interval
                execution_time=elapsed
            )
            
            self._history.record_benchmark(result)
            self._metrics.collect_benchmark_metrics(result)
            
            self._logger.info(f"Completed benchmark {request.benchmark_id} in {elapsed:.2f}s")
            return result
            
        finally:
            self._registry.unregister_benchmark(request.benchmark_id)

"""Metrics Collector Service.

Author: DriftAdapt Contributors
Purpose: Bridges validation statistics into the global MetricsBus telemetry pipeline.
"""

from typing import Any

from app.core.logging import LoggerFactory
from app.schemas.validation_result import ValidationResult
from app.schemas.benchmark_result import BenchmarkResult


class MetricsCollector:
    """Dispatches validation and benchmark outcomes to the system telemetry bus."""
    
    def __init__(self, metrics_bus: Any = None) -> None:
        self._logger = LoggerFactory.get_logger("ValidationMetricsCollector")
        self._metrics_bus = metrics_bus

    def collect_validation_metrics(self, result: ValidationResult) -> None:
        """Pushes validation sweep outcomes to telemetry."""
        if not self._metrics_bus or not hasattr(self._metrics_bus, "record"):
            return
            
        self._metrics_bus.record("validation.total_runs", 1)
        if result.success:
            self._metrics_bus.record("validation.success_rate", 1)
        else:
            self._metrics_bus.record("validation.failure_rate", 1)

    def collect_benchmark_metrics(self, result: BenchmarkResult) -> None:
        """Pushes performance metrics to telemetry."""
        if not self._metrics_bus or not hasattr(self._metrics_bus, "record"):
            return
            
        self._metrics_bus.record("benchmark.average_latency_ms", result.average_latency * 1000)
        self._metrics_bus.record("benchmark.tokens_per_second", result.throughput)
        self._metrics_bus.record("benchmark.memory_usage_mb", result.memory_usage)
        self._metrics_bus.record("benchmark.gpu_memory_mb", result.gpu_usage)
        self._metrics_bus.record("benchmark.cpu_usage_percent", result.cpu_usage)

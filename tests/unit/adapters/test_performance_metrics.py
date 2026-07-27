"""Tests for Performance Metrics.

Author: DriftAdapt Contributors
"""

import pytest

from app.adapters.metrics_registry import MetricsRegistry
from app.adapters.metrics_schema import PerformanceMetrics
from app.adapters.performance_metrics import PerformanceMetricsCalculator


def create_perf(merge_t: float, mem: float) -> PerformanceMetrics:
    return PerformanceMetrics(
        merge_time_ms=merge_t,
        load_time_ms=10.0,
        save_time_ms=10.0,
        validation_time_ms=5.0,
        checksum_time_ms=5.0,
        memory_usage_mb=mem,
        cpu_time_ms=100.0,
        peak_memory_mb=200.0
    )


def test_performance_metrics():
    registry = MetricsRegistry()
    calc = PerformanceMetricsCalculator(registry)
    
    assert calc.average_merge_time() == 0.0
    assert calc.average_memory_usage() == 0.0
    
    registry.add_performance_metrics(create_perf(100.0, 50.0))
    registry.add_performance_metrics(create_perf(200.0, 150.0))
    
    assert calc.average_merge_time() == 150.0
    assert calc.average_memory_usage() == 100.0

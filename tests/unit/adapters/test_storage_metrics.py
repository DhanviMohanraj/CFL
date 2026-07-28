"""Tests for Storage Metrics.

Author: DriftAdapt Contributors
"""

import pytest

from app.adapters.metrics_registry import MetricsRegistry
from app.adapters.metrics_schema import AdapterMetrics
from app.adapters.storage_metrics import StorageMetricsCalculator


def create_adapter(cid: str, size: int) -> AdapterMetrics:
    return AdapterMetrics(
        adapter_id="a1",
        clinic_id=cid,
        version_id=f"{cid}_v1",
        communication_round=1,
        parameter_count=100,
        adapter_size_bytes=1000,
        serialized_size_bytes=size,
        compressed_size_bytes=400,
        checksum="hash",
        storage_path="/tmp/test"
    )


def test_storage_metrics():
    registry = MetricsRegistry()
    calc = StorageMetricsCalculator(registry)
    
    # Empty
    assert calc.compute_total_storage_bytes() == 0
    assert calc.compute_average_adapter_size() == 0.0
    
    # Add metrics
    registry.add_adapter_metrics(create_adapter("c1", 1000))
    registry.add_adapter_metrics(create_adapter("c2", 2000))
    
    assert calc.compute_total_storage_bytes() == 3000
    assert calc.compute_average_adapter_size() == 1500.0
    
    per_clinic = calc.compute_storage_per_clinic()
    assert per_clinic["c1"] == 1000
    assert per_clinic["c2"] == 2000

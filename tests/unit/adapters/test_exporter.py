"""Tests for Metrics Exporter.

Author: DriftAdapt Contributors
"""

import json
from pathlib import Path

import pytest

from app.adapters.metrics_exporter import MetricsExporter
from app.adapters.metrics_registry import MetricsRegistry
from app.adapters.metrics_schema import AdapterMetrics


def create_adapter(cid: str) -> AdapterMetrics:
    return AdapterMetrics(
        adapter_id="a1",
        clinic_id=cid,
        version_id=f"{cid}_v1",
        communication_round=1,
        parameter_count=100,
        adapter_size_bytes=1000,
        serialized_size_bytes=800,
        compressed_size_bytes=400,
        checksum="hash",
        storage_path="/tmp/test"
    )


def test_export_json_csv(tmp_path: Path):
    registry = MetricsRegistry()
    registry.add_adapter_metrics(create_adapter("c1"))
    
    exporter = MetricsExporter(registry, tmp_path)
    
    json_path = exporter.export_json()
    assert json_path.exists()
    
    with open(json_path, "r") as f:
        data = json.load(f)
        assert len(data["adapters"]) == 1
        assert data["adapters"][0]["clinic_id"] == "c1"
        
    csv_path = exporter.export_csv()
    assert csv_path.exists()
    
    with open(csv_path, "r") as f:
        lines = f.readlines()
        assert len(lines) == 2  # Header + 1 row
        assert "c1" in lines[1]

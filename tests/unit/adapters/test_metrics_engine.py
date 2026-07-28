"""Tests for Adapter Metrics Engine.

Author: DriftAdapt Contributors
"""

import pytest

from app.adapters.metrics_engine import AdapterMetricsEngine
from app.adapters.metrics_schema import AdapterMetrics


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton instance before each test."""
    AdapterMetricsEngine._instance = None
    yield


def create_adapter(vid: str) -> AdapterMetrics:
    return AdapterMetrics(
        adapter_id="base",
        clinic_id="c1",
        version_id=vid,
        communication_round=1,
        parameter_count=100,
        adapter_size_bytes=1000,
        serialized_size_bytes=800,
        compressed_size_bytes=400,
        checksum="hash",
        storage_path="/tmp/test"
    )


def test_engine_singleton_and_recording():
    engine = AdapterMetricsEngine()
    
    engine.collector.record_adapter(create_adapter("v1"))
    
    history = engine._registry.get_adapter_history()
    assert len(history) == 1
    assert history[0].version_id == "v1"
    
    engine.reset()
    assert len(engine._registry.get_adapter_history()) == 0


from unittest.mock import patch

def test_bus_publishing():
    engine = AdapterMetricsEngine()
    
    with patch.object(engine._bus_publisher, 'publish') as mock_publish:
        engine.collector.record_adapter(create_adapter("v1"))
        
        engine.publish_to_bus()
        
        # Verify mock was called
        assert mock_publish.call_count > 0
        
        # Ensure specific keys are published
        published_keys = [call.args[0] for call in mock_publish.call_args_list]
        assert "storage.total.bytes" in published_keys
        assert "communication.upload.bytes" in published_keys

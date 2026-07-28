"""Tests for Adapter Collector.

Author: DriftAdapt Contributors
"""

import pytest
from app.federated.round_execution.adapter_collector import AdapterCollector
from app.federated.round_execution.execution_exceptions import AdapterCollectionError


def test_adapter_collector():
    collector = AdapterCollector()
    
    adapters = collector.collect_adapters(["c1", "c2"])
    assert len(adapters) == 2
    assert "c1" in adapters[0][0]
    
    with pytest.raises(AdapterCollectionError):
        collector.collect_adapters([])

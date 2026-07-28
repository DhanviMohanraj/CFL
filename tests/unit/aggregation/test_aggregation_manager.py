"""Tests for Aggregation Manager and Dispatcher.

Author: DriftAdapt Contributors
"""

from app.aggregation.aggregation_manager import AggregationManager
from app.aggregation.aggregation_registry import AggregationRegistry
from app.aggregation.aggregation_dispatcher import AggregationDispatcher


def test_aggregation_manager():
    registry = AggregationRegistry()
    manager = AggregationManager(registry)
    
    meta = manager.start_aggregation("r1", "fedavg", ["c1"])
    assert meta.round_id == "r1"
    
    manager.finish_aggregation("r1", success=True, version="v1")
    assert registry.lookup("r1").status == "COMPLETED"
    assert registry.lookup("r1").global_adapter_version == "v1"


def test_aggregation_dispatcher():
    class MockEngine:
        def aggregate(self, round_id, paths):
            return "success"
            
    dispatcher = AggregationDispatcher(MockEngine())
    res = dispatcher.dispatch("r1", ["path1"])
    assert res == "success"

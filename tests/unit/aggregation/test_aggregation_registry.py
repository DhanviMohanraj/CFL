"""Tests for Aggregation Registry.

Author: DriftAdapt Contributors
"""

from app.aggregation.aggregation_registry import AggregationRegistry
from app.aggregation.aggregation_schema import AggregationMetadata


def test_aggregation_registry():
    registry = AggregationRegistry()
    
    meta = AggregationMetadata(round_id="r1", algorithm="fedavg", participating_clinics=[])
    registry.register(meta)
    
    assert registry.lookup("r1") is not None
    
    stats = registry.statistics()
    assert stats["total_aggregations"] == 1
    
    registry.cleanup()
    assert registry.lookup("r1") is None

"""Tests for Aggregation Context and History.

Author: DriftAdapt Contributors
"""

from app.aggregation.aggregation_context import AggregationContext
from app.aggregation.aggregation_history import AggregationHistory


def test_aggregation_context():
    ctx = AggregationContext("r1", {}, ["c1"])
    ctx.add_adapter("c1", "path1", {"size": 100})
    assert len(ctx.adapter_paths) == 1
    assert ctx.adapter_metadata[0]["client_id"] == "c1"


def test_aggregation_history():
    history = AggregationHistory()
    history.record_aggregation("r1", "fedavg", ["c1"], 10.0, "v1", "hash")
    
    events = history.get_history()
    assert len(events) == 1
    assert events[0]["round_id"] == "r1"

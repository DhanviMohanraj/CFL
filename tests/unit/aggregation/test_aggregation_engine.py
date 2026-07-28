"""Tests for Aggregation Engine.

Author: DriftAdapt Contributors
"""

import pytest
from app.core.metrics.metrics_bus import MetricsBus
from app.aggregation.aggregation_engine import AggregationEngine


def test_aggregation_engine():
    bus = MetricsBus()
    config = {
        "algorithm": "fedavg",
        "validate_before_merge": True,
        "validate_after_merge": True,
        "save_history": True
    }
    
    engine = AggregationEngine(config, bus)
    
    engine.initialize("round_1", ["c1", "c2"])
    
    assert engine.status("round_1") == "STARTED"
    
    path = engine.aggregate("round_1", ["path1", "path2"])
    assert path == "exports/round_1_global_adapter.pt"
    
    assert engine.status("round_1") == "COMPLETED"

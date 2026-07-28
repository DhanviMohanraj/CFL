"""Tests for Adaptive Schema.

Author: DriftAdapt Contributors
"""

from app.adaptive.adaptive_schema import AdaptiveRecord


def test_adaptive_schema():
    record = AdaptiveRecord(
        decision_id="d1",
        participating_clinics=["c1"],
        strategy_name="ADAPTIVE_FEDAVG",
        weights={"c1": 1.0}
    )
    
    assert record.decision_id == "d1"
    assert record.strategy_name == "ADAPTIVE_FEDAVG"
    assert record.adaptation_id is not None

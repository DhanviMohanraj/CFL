"""Tests for Adaptive Engine.

Author: DriftAdapt Contributors
"""

import pytest
from app.core.metrics.metrics_bus import MetricsBus
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptive.adaptive_engine import AdaptiveFederationEngine
from app.adaptive.utilities.strategy_selector import StrategySelector
from app.adaptive.adaptive_exceptions import AdaptiveInitializationError


def test_adaptive_engine():
    bus = MetricsBus()
    selector = StrategySelector()
    engine = AdaptiveFederationEngine({}, bus, selector)
    
    decision = AdaptationDecision(
        decision_id="d1",
        drift_reports=[],
        affected_clinics=["c1"],
        adaptation_required=True,
        policy_name="GLOBAL",
        priority="HIGH",
        urgency="NEXT_ROUND",
        confidence=0.9,
        justification="test"
    )
    
    with pytest.raises(AdaptiveInitializationError):
        engine.execute(decision)
        
    engine.initialize()
    record = engine.execute(decision)
    
    assert record.strategy_name == "ADAPTIVE_FEDAVG"
    assert record.decision_id == "d1"
    assert "c1" in record.participating_clinics

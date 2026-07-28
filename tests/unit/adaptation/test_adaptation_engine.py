"""Tests for Adaptation Engine.

Author: DriftAdapt Contributors
"""

import pytest
from app.core.metrics.metrics_bus import MetricsBus
from app.drift.drift_schema import DriftReport
from app.adaptation.adaptation_engine import AdaptationEngine
from app.adaptation.policy_factory import PolicyFactory
from app.adaptation.policy_registry import PolicyRegistry
from app.adaptation.policies.no_adaptation import NoAdaptationPolicy
from app.adaptation.policies.local_policy import LocalPolicy
from app.adaptation.adaptation_exceptions import AdaptationInitializationError


def test_adaptation_engine():
    bus = MetricsBus()
    registry = PolicyRegistry()
    registry.register("no_adaptation", NoAdaptationPolicy())
    registry.register("local", LocalPolicy())
    factory = PolicyFactory(registry)
    
    engine = AdaptationEngine({}, bus, factory)
    
    report = DriftReport(clinic_id="c1", month=1, baseline_month=0, drift_detected=True)
    
    with pytest.raises(AdaptationInitializationError):
        engine.decide([report])
        
    engine.initialize()
    decision = engine.decide([report])
    
    assert decision.adaptation_required is True
    assert decision.policy_name == "LOCAL"

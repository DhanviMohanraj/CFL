"""Tests for Decision Engine.

Author: DriftAdapt Contributors
"""

from app.drift.drift_schema import DriftReport
from app.adaptation.decision_engine import DecisionEngine
from app.adaptation.policy_factory import PolicyFactory
from app.adaptation.policy_registry import PolicyRegistry
from app.adaptation.policies.no_adaptation import NoAdaptationPolicy
from app.adaptation.policies.local_policy import LocalPolicy


def test_decision_engine():
    registry = PolicyRegistry()
    registry.register("no_adaptation", NoAdaptationPolicy())
    registry.register("local", LocalPolicy())
    factory = PolicyFactory(registry)
    engine = DecisionEngine(factory)
    
    # Test No Adaptation
    report = DriftReport(clinic_id="c1", month=1, baseline_month=0, drift_detected=False)
    best_policy, score = engine.evaluate([report], {})
    assert isinstance(best_policy, NoAdaptationPolicy)
    assert score == 1.0
    
    # Test Local Adaptation
    report.drift_detected = True
    best_policy, score = engine.evaluate([report], {})
    assert isinstance(best_policy, LocalPolicy)
    assert score == 0.9

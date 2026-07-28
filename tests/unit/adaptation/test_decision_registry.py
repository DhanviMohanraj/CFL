"""Tests for Decision Registry and History.

Author: DriftAdapt Contributors
"""

from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptation.decision_registry import DecisionRegistry
from app.adaptation.decision_history import DecisionHistory


def test_decision_registry():
    registry = DecisionRegistry()
    decision = AdaptationDecision(
        decision_id="d1",
        adaptation_required=True,
        policy_name="LOCAL",
        priority="HIGH",
        urgency="IMMEDIATE",
        confidence=0.9,
        justification="test"
    )
    
    registry.register(decision)
    assert registry.lookup("d1") is not None
    assert registry.statistics()["total_decisions"] == 1


def test_decision_history():
    history = DecisionHistory()
    decision = AdaptationDecision(
        decision_id="d1",
        adaptation_required=True,
        policy_name="LOCAL",
        priority="HIGH",
        urgency="IMMEDIATE",
        confidence=0.9,
        justification="test"
    )
    
    history.record_decision(decision)
    assert len(history.get_history()) == 1

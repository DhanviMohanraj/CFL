"""Tests for Adaptation Schema.

Author: DriftAdapt Contributors
"""

from app.adaptation.adaptation_schema import AdaptationDecision


def test_adaptation_decision_schema():
    decision = AdaptationDecision(
        drift_reports=["r1"],
        affected_clinics=["c1"],
        adaptation_required=True,
        policy_name="LOCAL",
        priority="MEDIUM",
        urgency="NEXT_ROUND",
        confidence=0.9,
        justification="Test"
    )
    
    assert decision.adaptation_required is True
    assert decision.policy_name == "LOCAL"
    assert decision.decision_id is not None

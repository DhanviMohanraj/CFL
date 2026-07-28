"""Tests for Adaptation Scheduler and Priority.

Author: DriftAdapt Contributors
"""

from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptation.adaptation_scheduler import AdaptationScheduler
from app.adaptation.adaptation_priority import PriorityLevel, UrgencyLevel


def test_adaptation_scheduler():
    scheduler = AdaptationScheduler()
    
    decision = AdaptationDecision(
        decision_id="d1",
        adaptation_required=True,
        policy_name="LOCAL",
        priority=PriorityLevel.CRITICAL,
        urgency="",
        confidence=1.0,
        justification=""
    )
    
    assert scheduler.schedule(decision, {}) == UrgencyLevel.IMMEDIATE
    
    decision.priority = PriorityLevel.HIGH
    assert scheduler.schedule(decision, {}) == UrgencyLevel.NEXT_ROUND
    
    decision.priority = PriorityLevel.LOW
    decision.policy_name = "DEFERRED"
    assert scheduler.schedule(decision, {}) == UrgencyLevel.DEFERRED

"""Tests for Adaptive Utilities.

Author: DriftAdapt Contributors
"""

import pytest
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptive.utilities.strategy_selector import StrategySelector
from app.adaptive.strategies.adaptive_fedavg import AdaptiveFedAvg
from app.adaptive.strategies.cluster_based import ClusterBasedStrategy
from app.adaptive.strategies.priority_strategy import PriorityStrategy
from app.adaptive.strategies.selective_strategy import SelectiveStrategy


def get_decision(policy_name: str) -> AdaptationDecision:
    return AdaptationDecision(
        decision_id="d1",
        affected_clinics=["c1"],
        adaptation_required=True,
        policy_name=policy_name,
        priority="MEDIUM",
        urgency="NEXT_ROUND",
        confidence=0.9,
        justification="test"
    )


def test_strategy_selector():
    selector = StrategySelector()
    
    s1 = selector.select(get_decision("GLOBAL"), {})
    assert isinstance(s1, AdaptiveFedAvg)
    
    s2 = selector.select(get_decision("MULTI_CLINIC"), {})
    assert isinstance(s2, ClusterBasedStrategy)
    
    s3 = selector.select(get_decision("EMERGENCY"), {})
    assert isinstance(s3, PriorityStrategy)
    
    s4 = selector.select(get_decision("LOCAL"), {})
    assert isinstance(s4, SelectiveStrategy)
    
    s5 = selector.select(get_decision("UNKNOWN"), {"default_strategy": "adaptive_fedavg"})
    assert isinstance(s5, AdaptiveFedAvg)

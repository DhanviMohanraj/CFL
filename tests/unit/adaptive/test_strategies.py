"""Tests for Adaptive Strategies.

Author: DriftAdapt Contributors
"""

from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptive.strategies.severity_weighted import SeverityWeightedStrategy
from app.adaptive.strategies.cluster_based import ClusterBasedStrategy
from app.adaptive.strategies.regional_strategy import RegionalStrategy
from app.adaptive.strategies.priority_strategy import PriorityStrategy
from app.adaptive.strategies.selective_strategy import SelectiveStrategy
from app.adaptive.strategies.adaptive_fedavg import AdaptiveFedAvg
from app.adaptive.strategies.adaptive_fedprox import AdaptiveFedProx


def get_decision():
    return AdaptationDecision(
        decision_id="d1",
        affected_clinics=["c1", "c2"],
        adaptation_required=True,
        policy_name="LOCAL",
        priority="MEDIUM",
        urgency="NEXT_ROUND",
        confidence=0.9,
        justification="test"
    )


def test_severity_weighted_strategy():
    strategy = SeverityWeightedStrategy()
    record = strategy.execute(get_decision(), {})
    assert record.strategy_name == "SEVERITY_WEIGHTED"


def test_cluster_based_strategy():
    strategy = ClusterBasedStrategy()
    record = strategy.execute(get_decision(), {})
    assert record.strategy_name == "CLUSTER_BASED"


def test_regional_strategy():
    strategy = RegionalStrategy()
    record = strategy.execute(get_decision(), {})
    assert record.strategy_name == "REGIONAL"


def test_priority_strategy():
    strategy = PriorityStrategy()
    record = strategy.execute(get_decision(), {})
    assert record.strategy_name == "PRIORITY"


def test_selective_strategy():
    strategy = SelectiveStrategy()
    record = strategy.execute(get_decision(), {})
    assert record.strategy_name == "SELECTIVE"


def test_adaptive_fedavg_strategy():
    strategy = AdaptiveFedAvg()
    record = strategy.execute(get_decision(), {})
    assert record.strategy_name == "ADAPTIVE_FEDAVG"
    assert record.weights["c1"] == 0.5


def test_adaptive_fedprox_strategy():
    strategy = AdaptiveFedProx()
    record = strategy.execute(get_decision(), {})
    assert record.strategy_name == "ADAPTIVE_FEDPROX"

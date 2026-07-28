"""DriftAdapt Strategy Selector.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptive.strategies.base_strategy import BaseStrategy
from app.adaptive.strategies.severity_weighted import SeverityWeightedStrategy
from app.adaptive.strategies.cluster_based import ClusterBasedStrategy
from app.adaptive.strategies.regional_strategy import RegionalStrategy
from app.adaptive.strategies.priority_strategy import PriorityStrategy
from app.adaptive.strategies.selective_strategy import SelectiveStrategy
from app.adaptive.strategies.adaptive_fedavg import AdaptiveFedAvg
from app.adaptive.strategies.adaptive_fedprox import AdaptiveFedProx
from app.adaptive.adaptive_exceptions import StrategySelectionError


class StrategySelector:
    """Selects the appropriate adaptive aggregation strategy."""
    
    def __init__(self) -> None:
        self.strategies = {
            "severity_weighted": SeverityWeightedStrategy(),
            "cluster_based": ClusterBasedStrategy(),
            "regional": RegionalStrategy(),
            "priority": PriorityStrategy(),
            "selective": SelectiveStrategy(),
            "adaptive_fedavg": AdaptiveFedAvg(),
            "adaptive_fedprox": AdaptiveFedProx()
        }
        
    def select(self, decision: AdaptationDecision, config: Dict[str, Any]) -> BaseStrategy:
        """Automatically chooses an aggregation strategy."""
        default_strategy = config.get("default_strategy", "adaptive_fedavg")
        
        # Policy-driven selection
        policy_name = decision.policy_name.lower()
        if "global" in policy_name:
            strategy_name = "adaptive_fedavg"
        elif "multi_clinic" in policy_name:
            strategy_name = "cluster_based"
        elif "emergency" in policy_name:
            strategy_name = "priority"
        elif "local" in policy_name:
            strategy_name = "selective"
        else:
            strategy_name = default_strategy
            
        strategy = self.strategies.get(strategy_name)
        if not strategy:
            raise StrategySelectionError(f"Strategy {strategy_name} not found.")
            
        return strategy

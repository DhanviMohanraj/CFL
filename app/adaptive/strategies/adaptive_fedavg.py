"""DriftAdapt Adaptive FedAvg Strategy.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptive.adaptive_schema import AdaptiveRecord
from app.adaptive.strategies.base_strategy import BaseStrategy


class AdaptiveFedAvg(BaseStrategy):
    """Extension of FedAvg supporting adaptive weights and selective participation."""
    
    def execute(self, decision: AdaptationDecision, config: Dict[str, Any]) -> AdaptiveRecord:
        clinics = decision.affected_clinics
        weights = {c: 1.0 / len(clinics) for c in clinics} if clinics else {}
        
        return AdaptiveRecord(
            decision_id=decision.decision_id,
            participating_clinics=clinics,
            strategy_name="ADAPTIVE_FEDAVG",
            weights=weights
        )

"""DriftAdapt Priority Strategy.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptive.adaptive_schema import AdaptiveRecord
from app.adaptive.strategies.base_strategy import BaseStrategy


class PriorityStrategy(BaseStrategy):
    """Aggregation strategy prioritizing critical clinics."""
    
    def execute(self, decision: AdaptationDecision, config: Dict[str, Any]) -> AdaptiveRecord:
        return AdaptiveRecord(
            decision_id=decision.decision_id,
            participating_clinics=decision.affected_clinics,
            strategy_name="PRIORITY"
        )

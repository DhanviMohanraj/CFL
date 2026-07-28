"""DriftAdapt No Adaptation Policy.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any
from app.drift.drift_schema import DriftReport
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptation.policies.base_policy import BasePolicy


class NoAdaptationPolicy(BasePolicy):
    """Policy that recommends no adaptation."""
    
    def is_applicable(self, reports: List[DriftReport], config: Dict[str, Any]) -> bool:
        return True
        
    def evaluate(self, reports: List[DriftReport], config: Dict[str, Any]) -> float:
        drifts = [r for r in reports if r.drift_detected]
        if not drifts:
            return 1.0
        return 0.1
        
    def generate_decision(self, reports: List[DriftReport], confidence: float, config: Dict[str, Any]) -> AdaptationDecision:
        return AdaptationDecision(
            drift_reports=[],
            affected_clinics=[],
            adaptation_required=False,
            policy_name="NO_ADAPTATION",
            priority="LOW",
            urgency="DEFERRED",
            confidence=confidence,
            justification="No significant drift detected across reporting clinics."
        )

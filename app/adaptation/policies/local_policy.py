"""DriftAdapt Local Policy.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any
from app.drift.drift_schema import DriftReport
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptation.policies.base_policy import BasePolicy


class LocalPolicy(BasePolicy):
    """Policy that recommends adaptation only for affected individual clinics."""
    
    def is_applicable(self, reports: List[DriftReport], config: Dict[str, Any]) -> bool:
        return any(r.drift_detected for r in reports)
        
    def evaluate(self, reports: List[DriftReport], config: Dict[str, Any]) -> float:
        drifting_clinics = sum(1 for r in reports if r.drift_detected)
        if drifting_clinics == 1:
            return 0.9 # Highly confident if only one clinic drifted
        elif drifting_clinics > 1:
            return 0.6
        return 0.0
        
    def generate_decision(self, reports: List[DriftReport], confidence: float, config: Dict[str, Any]) -> AdaptationDecision:
        affected = [r.clinic_id for r in reports if r.drift_detected]
        return AdaptationDecision(
            drift_reports=[],
            affected_clinics=affected,
            adaptation_required=True,
            policy_name="LOCAL",
            priority="MEDIUM",
            urgency="NEXT_ROUND",
            confidence=confidence,
            justification=f"Localized drift detected in clinics: {', '.join(affected)}."
        )

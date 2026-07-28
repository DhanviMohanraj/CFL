"""DriftAdapt Global Policy.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any
from app.drift.drift_schema import DriftReport
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptation.policies.base_policy import BasePolicy


class GlobalPolicy(BasePolicy):
    """Policy that recommends federated adaptation when drift is widespread."""
    
    def is_applicable(self, reports: List[DriftReport], config: Dict[str, Any]) -> bool:
        threshold = config.get("global_clinic_threshold", 3)
        drifting_clinics = sum(1 for r in reports if r.drift_detected)
        return drifting_clinics >= threshold
        
    def evaluate(self, reports: List[DriftReport], config: Dict[str, Any]) -> float:
        drifting_clinics = sum(1 for r in reports if r.drift_detected)
        total_clinics = len(reports)
        if total_clinics > 0 and drifting_clinics == total_clinics:
            return 1.0 # Absolute confidence if all clinics drift
        elif total_clinics > 0 and drifting_clinics >= config.get("global_clinic_threshold", 3):
            return 0.85
        return 0.0
        
    def generate_decision(self, reports: List[DriftReport], confidence: float, config: Dict[str, Any]) -> AdaptationDecision:
        affected = [r.clinic_id for r in reports if r.drift_detected]
        return AdaptationDecision(
            drift_reports=[],
            affected_clinics=affected,
            adaptation_required=True,
            policy_name="GLOBAL",
            priority="HIGH",
            urgency="NEXT_ROUND",
            confidence=confidence,
            justification="Widespread drift detected. Global federated update recommended."
        )

"""DriftAdapt Multi-Clinic Policy.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any
from app.drift.drift_schema import DriftReport
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptation.policies.base_policy import BasePolicy


class MultiClinicPolicy(BasePolicy):
    """Policy for joint adaptation when multiple, but not all, clinics drift."""
    
    def is_applicable(self, reports: List[DriftReport], config: Dict[str, Any]) -> bool:
        drifting_clinics = sum(1 for r in reports if r.drift_detected)
        return drifting_clinics >= 2
        
    def evaluate(self, reports: List[DriftReport], config: Dict[str, Any]) -> float:
        drifting_clinics = sum(1 for r in reports if r.drift_detected)
        total_clinics = len(reports)
        if total_clinics > 0 and 1 < drifting_clinics < total_clinics:
            return 0.8
        return 0.0
        
    def generate_decision(self, reports: List[DriftReport], confidence: float, config: Dict[str, Any]) -> AdaptationDecision:
        affected = [r.clinic_id for r in reports if r.drift_detected]
        return AdaptationDecision(
            drift_reports=[],
            affected_clinics=affected,
            adaptation_required=True,
            policy_name="MULTI_CLINIC",
            priority="HIGH",
            urgency="NEXT_ROUND",
            confidence=confidence,
            justification=f"Correlated drift detected in multiple clinics: {', '.join(affected)}."
        )

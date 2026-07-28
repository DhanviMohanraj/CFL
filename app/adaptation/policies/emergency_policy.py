"""DriftAdapt Emergency Policy.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any
from app.drift.drift_schema import DriftReport
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptation.policies.base_policy import BasePolicy


class EmergencyPolicy(BasePolicy):
    """Policy that triggers immediate adaptation for severe drift."""
    
    def is_applicable(self, reports: List[DriftReport], config: Dict[str, Any]) -> bool:
        return any(r.severity == "SIGNIFICANT" for r in reports)
        
    def evaluate(self, reports: List[DriftReport], config: Dict[str, Any]) -> float:
        severe_drifts = sum(1 for r in reports if r.severity == "SIGNIFICANT")
        if severe_drifts > 0:
            # High confidence due to urgency
            return min(0.7 + (severe_drifts * 0.1), 1.0)
        return 0.0
        
    def generate_decision(self, reports: List[DriftReport], confidence: float, config: Dict[str, Any]) -> AdaptationDecision:
        affected = [r.clinic_id for r in reports if r.severity == "SIGNIFICANT"]
        return AdaptationDecision(
            drift_reports=[],
            affected_clinics=affected,
            adaptation_required=True,
            policy_name="EMERGENCY",
            priority="CRITICAL",
            urgency="IMMEDIATE",
            confidence=confidence,
            justification=f"Severe drift detected in clinics: {', '.join(affected)}. Immediate adaptation required."
        )

"""DriftAdapt Progressive Policy.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any
from app.drift.drift_schema import DriftReport
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptation.policies.base_policy import BasePolicy


class ProgressivePolicy(BasePolicy):
    """Policy for gradual adaptation for slowly evolving trends."""
    
    def is_applicable(self, reports: List[DriftReport], config: Dict[str, Any]) -> bool:
        if not config.get("progressive_enabled", True):
            return False
        # Applicable if drift is moderate and not widespread
        return any(r.severity == "MODERATE" for r in reports)
        
    def evaluate(self, reports: List[DriftReport], config: Dict[str, Any]) -> float:
        moderate_drifts = sum(1 for r in reports if r.severity == "MODERATE")
        severe_drifts = sum(1 for r in reports if r.severity == "SIGNIFICANT")
        if severe_drifts == 0 and moderate_drifts > 0:
            return 0.75
        return 0.0
        
    def generate_decision(self, reports: List[DriftReport], confidence: float, config: Dict[str, Any]) -> AdaptationDecision:
        affected = [r.clinic_id for r in reports if r.severity == "MODERATE"]
        return AdaptationDecision(
            drift_reports=[],
            affected_clinics=affected,
            adaptation_required=True,
            policy_name="PROGRESSIVE",
            priority="LOW",
            urgency="NEXT_ROUND",
            confidence=confidence,
            justification="Moderate drift detected. Gradual progressive adaptation recommended."
        )

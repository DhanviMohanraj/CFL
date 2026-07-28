"""DriftAdapt Deferred Policy.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any
from app.drift.drift_schema import DriftReport
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptation.policies.base_policy import BasePolicy


class DeferredPolicy(BasePolicy):
    """Policy to postpone adaptation if drift is weak or unstable."""
    
    def is_applicable(self, reports: List[DriftReport], config: Dict[str, Any]) -> bool:
        if not config.get("deferred_enabled", True):
            return False
        return any(r.drift_detected and r.severity == "LOW" for r in reports)
        
    def evaluate(self, reports: List[DriftReport], config: Dict[str, Any]) -> float:
        weak_drifts = sum(1 for r in reports if r.drift_detected and r.severity == "LOW")
        severe_drifts = sum(1 for r in reports if r.severity in ["MODERATE", "SIGNIFICANT"])
        
        if severe_drifts == 0 and weak_drifts > 0:
            return 0.8
        return 0.0
        
    def generate_decision(self, reports: List[DriftReport], confidence: float, config: Dict[str, Any]) -> AdaptationDecision:
        return AdaptationDecision(
            drift_reports=[],
            affected_clinics=[],
            adaptation_required=False,
            policy_name="DEFERRED",
            priority="LOW",
            urgency="DEFERRED",
            confidence=confidence,
            justification="Drift is weak or unstable. Adaptation deferred."
        )

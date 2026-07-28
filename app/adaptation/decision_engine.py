"""DriftAdapt Decision Engine.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any, Tuple
from app.drift.drift_schema import DriftReport
from app.adaptation.adaptation_exceptions import DecisionGenerationError
from app.adaptation.policy_factory import PolicyFactory


class DecisionEngine:
    """Evaluates drift reports against policies to produce adaptation decisions."""
    
    def __init__(self, policy_factory: PolicyFactory) -> None:
        self.policy_factory = policy_factory
        
    def evaluate(self, reports: List[DriftReport], config: Dict[str, Any]) -> Tuple[Any, float]:
        """Evaluates reports against all policies and selects the best one."""
        if not reports:
            raise DecisionGenerationError("No reports provided for evaluation.")
            
        # Get all policies
        policies = self.policy_factory.get_all_policies()
        
        best_policy = None
        highest_score = -1.0
        
        for name, policy in policies.items():
            if not policy.is_applicable(reports, config):
                continue
                
            score = policy.evaluate(reports, config)
            if score > highest_score:
                highest_score = score
                best_policy = policy
                
        if not best_policy:
            best_policy = self.policy_factory.get_policy("no_adaptation")
            highest_score = 1.0
            
        return best_policy, highest_score

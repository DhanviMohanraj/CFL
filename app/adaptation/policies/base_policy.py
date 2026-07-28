"""DriftAdapt Base Policy.

Author: DriftAdapt Contributors
"""

import abc
from typing import List, Dict, Any
from app.drift.drift_schema import DriftReport
from app.adaptation.adaptation_schema import AdaptationDecision


class BasePolicy(abc.ABC):
    """Abstract base class for all adaptation policies."""
    
    @abc.abstractmethod
    def is_applicable(self, reports: List[DriftReport], config: Dict[str, Any]) -> bool:
        """Determines if the policy applies to the given drift reports."""
        pass
        
    @abc.abstractmethod
    def evaluate(self, reports: List[DriftReport], config: Dict[str, Any]) -> float:
        """Returns a confidence score for this policy (0.0 to 1.0)."""
        pass
        
    @abc.abstractmethod
    def generate_decision(self, reports: List[DriftReport], confidence: float, config: Dict[str, Any]) -> AdaptationDecision:
        """Generates the structured adaptation decision."""
        pass

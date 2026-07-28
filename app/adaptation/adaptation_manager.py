"""DriftAdapt Adaptation Manager.

Author: DriftAdapt Contributors
"""

from app.adaptation.decision_registry import DecisionRegistry
from app.adaptation.adaptation_schema import AdaptationDecision


class AdaptationManager:
    """Manages the state and tracking of adaptation decisions."""
    
    def __init__(self, registry: DecisionRegistry) -> None:
        self.registry = registry
        
    def track_decision(self, decision: AdaptationDecision) -> None:
        """Registers a completed adaptation decision."""
        self.registry.register(decision)

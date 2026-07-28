"""DriftAdapt Policy Visualizer.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any
from app.adaptation.adaptation_schema import AdaptationDecision


class PolicyVisualizer:
    """Placeholder for visualizing adaptation decisions."""
    
    @staticmethod
    def summarize(decision: AdaptationDecision) -> Dict[str, Any]:
        """Creates a dashboard-friendly summary of the decision."""
        return {
            "policy": decision.policy_name,
            "priority": decision.priority,
            "urgency": decision.urgency,
            "clinics": decision.affected_clinics,
            "confidence": f"{decision.confidence * 100:.1f}%",
            "justification": decision.justification
        }

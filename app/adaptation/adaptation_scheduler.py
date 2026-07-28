"""DriftAdapt Adaptation Scheduler.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptation.adaptation_priority import UrgencyLevel


class AdaptationScheduler:
    """Determines execution schedules for adaptation decisions."""
    
    def schedule(self, decision: AdaptationDecision, config: Dict[str, Any]) -> str:
        """Determines the appropriate scheduling urgency."""
        if decision.priority == "CRITICAL":
            return UrgencyLevel.IMMEDIATE
        elif decision.priority == "HIGH":
            return UrgencyLevel.NEXT_ROUND
        elif decision.policy_name.lower() == "deferred":
            return UrgencyLevel.DEFERRED
        else:
            return UrgencyLevel.NEXT_ROUND

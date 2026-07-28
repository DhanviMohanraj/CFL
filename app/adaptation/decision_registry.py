"""DriftAdapt Decision Registry.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, List, Optional
from app.adaptation.adaptation_schema import AdaptationDecision


class DecisionRegistry:
    """Manages tracking of generated adaptation decisions."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._decisions: Dict[str, AdaptationDecision] = {}
        
    def register(self, decision: AdaptationDecision) -> None:
        with self._lock:
            self._decisions[decision.decision_id] = decision
            
    def lookup(self, decision_id: str) -> Optional[AdaptationDecision]:
        with self._lock:
            return self._decisions.get(decision_id)
            
    def history(self) -> List[AdaptationDecision]:
        with self._lock:
            return list(self._decisions.values())
            
    def statistics(self) -> Dict[str, int]:
        with self._lock:
            return {
                "total_decisions": len(self._decisions),
                "adaptations_required": sum(1 for d in self._decisions.values() if d.adaptation_required)
            }
            
    def cleanup(self) -> None:
        with self._lock:
            self._decisions.clear()

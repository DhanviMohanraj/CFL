"""DriftAdapt Decision History.

Author: DriftAdapt Contributors
"""

import threading
from typing import List
from app.adaptation.adaptation_schema import AdaptationDecision


class DecisionHistory:
    """Persists historical adaptation decisions."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._history: List[AdaptationDecision] = []
        
    def record_decision(self, decision: AdaptationDecision) -> None:
        """Records a completed decision."""
        with self._lock:
            self._history.append(decision)
            
    def get_history(self) -> List[AdaptationDecision]:
        """Returns the recorded decision history."""
        with self._lock:
            return list(self._history)

"""DriftAdapt Privacy Accountant.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, Any
from app.knowledge.consolidation_exceptions import PrivacyBudgetExceededError


class PrivacyAccountant:
    """Tracks privacy budget consumption."""
    
    def __init__(self, epsilon_budget: float = 8.0, delta: float = 1e-5) -> None:
        self._budget = epsilon_budget
        self._delta = delta
        self._consumed = 0.0
        self._lock = threading.RLock()
        
    def consume(self, amount: float) -> None:
        with self._lock:
            if self._consumed + amount > self._budget:
                raise PrivacyBudgetExceededError(f"Privacy budget exceeded. Budget: {self._budget}, Consumed: {self._consumed}, Requested: {amount}")
            self._consumed += amount
            
    def get_remaining(self) -> float:
        with self._lock:
            return self._budget - self._consumed

"""DriftAdapt Base Strategy.

Author: DriftAdapt Contributors
"""

import abc
from typing import Dict, Any
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptive.adaptive_schema import AdaptiveRecord


class BaseStrategy(abc.ABC):
    """Abstract base class for all adaptive aggregation strategies."""
    
    @abc.abstractmethod
    def execute(self, decision: AdaptationDecision, config: Dict[str, Any]) -> AdaptiveRecord:
        """Executes the strategy and returns an execution record."""
        pass

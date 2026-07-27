"""DriftAdapt Merge Strategy Interface.

Author: DriftAdapt Contributors
Purpose: Defines the abstract interface for all federated aggregation algorithms.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AdapterMergeStrategy(ABC):
    """Abstract base class for all adapter merge algorithms."""

    @abstractmethod
    def merge(self, states: List[Dict[str, Any]], weights: Optional[List[float]] = None) -> Dict[str, Any]:
        """Merges a list of adapter state dictionaries into a single state dictionary.
        
        Args:
            states: A list of state dictionaries (tensors) from participating clients.
            weights: Optional list of relative importance weights per client.
            
        Returns:
            The merged state dictionary.
        """
        pass

    @abstractmethod
    def validate_inputs(self, states: List[Dict[str, Any]]) -> None:
        """Validates that the input states are suitable for this specific strategy.
        
        This complements the base MergeValidator, allowing strategies to enforce
        their own mathematical constraints.
        """
        pass

    @abstractmethod
    def supports_weighting(self) -> bool:
        """Returns True if this strategy supports custom client weighting."""
        pass

    @abstractmethod
    def strategy_name(self) -> str:
        """Returns the identifier name of the strategy."""
        pass

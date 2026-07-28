"""Base Aggregator Strategy.

Author: DriftAdapt Contributors
Purpose: Defines the abstract contract for all federated aggregation algorithms (FedAvg, FedProx, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from app.schemas.client_update_record import ClientUpdateRecord


class BaseAggregator(ABC):
    """Abstract base class for federated aggregation strategies."""
    
    @abstractmethod
    def aggregate(
        self,
        state_dicts: List[Dict[str, Any]],
        weights: List[float],
        global_state_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Merges a list of client state dicts into a new global state dict.
        
        Args:
            state_dicts: A list of strictly validated PyTorch state dictionaries (LoRA parameters).
            weights: The relative contribution weight of each state dict (must sum to 1.0 or be normalized).
            global_state_dict: The current global weights (useful for algorithms like Scaffold or FedProx).
            
        Returns:
            A new dictionary representing the aggregated global PyTorch state dict.
            
        Raises:
            ValueError: If the aggregation fails due to mathematical or tensor shape incompatibilities.
        """
        pass
    
    @property
    @abstractmethod
    def algorithm_name(self) -> str:
        """Returns the canonical string identifier for this algorithm."""
        pass

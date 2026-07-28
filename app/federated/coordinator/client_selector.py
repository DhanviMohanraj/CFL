"""DriftAdapt Client Selector.

Author: DriftAdapt Contributors
"""

import random
from abc import ABC, abstractmethod
from typing import List

from app.federated.coordinator.coordinator_exceptions import ClientSelectionError


class ClientSelectionStrategy(ABC):
    """Abstract strategy for selecting clients for a federated round."""
    
    @abstractmethod
    def select(self, available_clients: List[str], **kwargs) -> List[str]:
        """Selects a subset of clients."""
        pass


class AllClientsStrategy(ClientSelectionStrategy):
    """Selects all available clients."""
    
    def select(self, available_clients: List[str], **kwargs) -> List[str]:
        if not available_clients:
            raise ClientSelectionError("No clients available for selection.")
        return list(available_clients)


class RandomSubsetStrategy(ClientSelectionStrategy):
    """Selects a random subset of clients."""
    
    def select(self, available_clients: List[str], subset_size: int = 1, **kwargs) -> List[str]:
        if not available_clients:
            raise ClientSelectionError("No clients available for selection.")
        if subset_size > len(available_clients):
            subset_size = len(available_clients)
        return random.sample(available_clients, subset_size)


class PercentageParticipationStrategy(ClientSelectionStrategy):
    """Selects a percentage of available clients."""
    
    def select(self, available_clients: List[str], percentage: float = 1.0, **kwargs) -> List[str]:
        if not available_clients:
            raise ClientSelectionError("No clients available for selection.")
        if percentage <= 0.0 or percentage > 1.0:
            raise ClientSelectionError(f"Invalid percentage: {percentage}")
            
        subset_size = max(1, int(len(available_clients) * percentage))
        return random.sample(available_clients, subset_size)

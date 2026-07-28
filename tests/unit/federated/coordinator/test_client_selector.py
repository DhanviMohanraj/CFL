"""Tests for Client Selector.

Author: DriftAdapt Contributors
"""

import pytest

from app.federated.coordinator.client_selector import (
    AllClientsStrategy,
    RandomSubsetStrategy,
    PercentageParticipationStrategy,
)
from app.federated.coordinator.coordinator_exceptions import ClientSelectionError


def test_all_clients_strategy():
    strategy = AllClientsStrategy()
    clients = ["c1", "c2", "c3"]
    
    selected = strategy.select(clients)
    assert set(selected) == set(clients)
    
    with pytest.raises(ClientSelectionError):
        strategy.select([])


def test_random_subset_strategy():
    strategy = RandomSubsetStrategy()
    clients = ["c1", "c2", "c3"]
    
    selected = strategy.select(clients, subset_size=2)
    assert len(selected) == 2
    for s in selected:
        assert s in clients
        
    selected = strategy.select(clients, subset_size=5)
    assert len(selected) == 3


def test_percentage_strategy():
    strategy = PercentageParticipationStrategy()
    clients = ["c1", "c2", "c3", "c4"]
    
    selected = strategy.select(clients, percentage=0.5)
    assert len(selected) == 2
    
    selected = strategy.select(clients, percentage=1.0)
    assert len(selected) == 4
    
    with pytest.raises(ClientSelectionError):
        strategy.select(clients, percentage=1.5)

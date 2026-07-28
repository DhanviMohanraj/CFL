"""Tests for Round Manager.

Author: DriftAdapt Contributors
"""

import pytest

from app.federated.coordinator.round_manager import RoundManager
from app.federated.coordinator.coordinator_registry import CoordinatorRegistry
from app.federated.coordinator.coordinator_exceptions import RoundInitializationError


def test_round_manager_lifecycle():
    registry = CoordinatorRegistry()
    manager = RoundManager(registry)
    
    assert manager.current_round() is None
    
    clients = ["c1", "c2"]
    round_meta = manager.begin_round(clients)
    
    assert round_meta.global_round == 1
    assert round_meta.selected_clients == clients
    assert round_meta.status == "INITIALIZED"
    
    assert manager.current_round() == round_meta
    
    with pytest.raises(RoundInitializationError):
        manager.begin_round(["c3"])
        
    manager.finish_round(success=True)
    
    assert manager.current_round() is None
    
    history = manager.history()
    assert len(history) == 1
    assert history[0].status == "COMPLETED"
    
    stats = registry.statistics()
    assert stats.total_rounds == 1
    assert stats.successful_rounds == 1

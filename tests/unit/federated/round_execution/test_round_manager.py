"""Tests for Round Manager.

Author: DriftAdapt Contributors
"""

from app.federated.round_execution.round_manager import RoundManager
from app.federated.round_execution.round_registry import RoundRegistry


def test_round_manager():
    registry = RoundRegistry()
    manager = RoundManager(registry)
    
    round_id = manager.start_round(month=1, epoch=1, clients=["c1"])
    assert round_id is not None
    
    meta = registry.lookup(round_id)
    assert meta.status == "STARTED"
    
    manager.finish_round(round_id, success=True)
    meta = registry.lookup(round_id)
    assert meta.status == "COMPLETED"
    
    round_id_2 = manager.start_round(month=2, epoch=1, clients=["c2"])
    manager.cancel_round(round_id_2)
    meta2 = registry.lookup(round_id_2)
    assert meta2.status == "CANCELLED"

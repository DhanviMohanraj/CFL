"""Tests for Round Registry.

Author: DriftAdapt Contributors
"""

from app.federated.round_execution.round_registry import RoundRegistry
from app.federated.round_execution.execution_schema import RoundMetadata


def test_round_registry():
    registry = RoundRegistry()
    
    meta = RoundMetadata(round_id="r1", month=1, participating_clinics=["c1"])
    registry.register(meta)
    
    assert registry.lookup("r1") is not None
    assert registry.lookup("r2") is None
    
    registry.archive("r1")
    assert registry.lookup("r1") is not None
    
    stats = registry.statistics()
    assert stats["active_rounds"] == 0
    assert stats["historical_rounds"] == 1

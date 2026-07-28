"""Tests for Adaptive Registry and History.

Author: DriftAdapt Contributors
"""

import pytest
from app.adaptive.adaptive_schema import AdaptiveRecord
from app.adaptive.adaptive_registry import AdaptiveRegistry
from app.adaptive.adaptive_history import AdaptiveHistory
from app.adaptive.adaptive_exceptions import RegistryError


def test_adaptive_registry():
    registry = AdaptiveRegistry()
    record = AdaptiveRecord(
        decision_id="d1",
        participating_clinics=["c1"],
        strategy_name="ADAPTIVE_FEDAVG"
    )
    
    registry.register(record)
    assert registry.lookup(record.adaptation_id) is not None
    assert registry.statistics()["total_adaptations"] == 1
    
    with pytest.raises(RegistryError):
        registry.register(record)


def test_adaptive_history():
    history = AdaptiveHistory()
    record = AdaptiveRecord(
        decision_id="d1",
        participating_clinics=["c1"],
        strategy_name="ADAPTIVE_FEDAVG"
    )
    
    history.record_execution(record)
    assert len(history.get_history()) == 1

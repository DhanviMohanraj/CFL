"""Tests for Knowledge Consolidation.

Author: DriftAdapt Contributors
"""

import pytest
from app.knowledge.consolidation_schema import ConsolidationRecord
from app.knowledge.consolidation_registry import ConsolidationRegistry
from app.knowledge.consolidation_history import ConsolidationHistory
from app.knowledge.consolidation_validator import ConsolidationValidator
from app.knowledge.consolidation_exceptions import KnowledgeConsolidationError, RegistryError
from app.knowledge.consolidation_engine import KnowledgeConsolidationEngine
from app.core.metrics.metrics_bus import MetricsBus


def test_consolidation_schema():
    record = ConsolidationRecord(
        round_id=1,
        adaptive_global_adapter_path="path/to/adapter",
        strategy_name="simple"
    )
    assert record.round_id == 1
    assert record.strategy_name == "simple"
    assert record.consolidation_id is not None


def test_consolidation_registry():
    registry = ConsolidationRegistry()
    record = ConsolidationRecord(
        round_id=1,
        adaptive_global_adapter_path="path",
        strategy_name="simple"
    )
    
    registry.register(record)
    assert registry.lookup(record.consolidation_id) is not None
    assert registry.statistics()["total_consolidations"] == 1
    
    with pytest.raises(RegistryError):
        registry.register(record)


def test_consolidation_history():
    history = ConsolidationHistory()
    record = ConsolidationRecord(
        round_id=1,
        adaptive_global_adapter_path="path",
        strategy_name="simple"
    )
    history.record_consolidation(record)
    assert len(history.get_history()) == 1


def test_consolidation_validator():
    validator = ConsolidationValidator()
    
    with pytest.raises(KnowledgeConsolidationError):
        validator.validate(-1, "path")
        
    with pytest.raises(KnowledgeConsolidationError):
        validator.validate(1, "")
        
    validator.validate(1, "path")


def test_consolidation_engine():
    bus = MetricsBus()
    config = {"knowledge": {"consolidation_strategy": "simple"}}
    engine = KnowledgeConsolidationEngine(config, bus)
    
    with pytest.raises(KnowledgeConsolidationError):
        engine.consolidate(1, "path")
        
    engine.initialize()
    record = engine.consolidate(1, "path")
    assert record.strategy_name == "simple"
    assert record.round_id == 1

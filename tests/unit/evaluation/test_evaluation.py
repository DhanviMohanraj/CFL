"""Tests for Evaluation.

Author: DriftAdapt Contributors
"""

import pytest
from app.core.metrics.metrics_bus import MetricsBus
from app.evaluation.evaluation_schema import EvaluationRecord
from app.evaluation.benchmark_registry import BenchmarkRegistry
from app.evaluation.evaluation_exceptions import RegistryError, EvaluationError
from app.evaluation.evaluation_engine import EvaluationEngine


def test_evaluation_schema():
    record = EvaluationRecord(experiment_id="e1")
    assert record.experiment_id == "e1"
    assert record.evaluation_id is not None


def test_benchmark_registry():
    registry = BenchmarkRegistry()
    record = EvaluationRecord(experiment_id="e1")
    
    registry.register(record)
    assert registry.lookup(record.evaluation_id) is not None
    assert registry.statistics()["total_records"] == 1
    
    with pytest.raises(RegistryError):
        registry.register(record)


def test_evaluation_engine():
    bus = MetricsBus()
    engine = EvaluationEngine({}, bus)
    
    with pytest.raises(EvaluationError):
        engine.evaluate("e1", {})
        
    engine.initialize()
    record = engine.evaluate("e1", {})
    assert record.experiment_id == "e1"

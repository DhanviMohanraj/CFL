"""Tests for Experiment Registry.

Author: DriftAdapt Contributors
"""

from app.training.experiment_registry import ExperimentRegistry
from app.training.experiment_schema import ExperimentMetadata


def test_experiment_registry():
    registry = ExperimentRegistry()
    
    metadata = ExperimentMetadata(
        experiment_id="exp_1",
        name="test_exp"
    )
    
    registry.register(metadata)
    
    assert registry.lookup("exp_1") is not None
    assert registry.lookup("exp_2") is None
    
    registry.archive("exp_1")
    assert registry.lookup("exp_1") is not None
    
    stats = registry.statistics()
    assert stats["active_count"] == 0
    assert stats["archived_count"] == 1
    
    registry.cleanup()
    assert registry.lookup("exp_1") is None

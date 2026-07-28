"""Tests for Analytics.

Author: DriftAdapt Contributors
"""

import pytest
from app.core.metrics.metrics_bus import MetricsBus
from app.analytics.analytics_schema import AnalyticsRecord
from app.analytics.analytics_registry import AnalyticsRegistry
from app.analytics.analytics_exceptions import RegistryError, AnalyticsInitializationError
from app.analytics.analytics_engine import AnalyticsEngine


def test_analytics_schema():
    record = AnalyticsRecord(round_id=1, experiment_id="e1")
    assert record.round_id == 1
    assert record.experiment_id == "e1"
    assert record.record_id is not None


def test_analytics_registry():
    registry = AnalyticsRegistry()
    record = AnalyticsRecord(round_id=1, experiment_id="e1")
    
    registry.register(record)
    assert registry.lookup(record.record_id) is not None
    assert registry.statistics()["total_records"] == 1
    
    with pytest.raises(RegistryError):
        registry.register(record)


def test_analytics_engine():
    bus = MetricsBus()
    engine = AnalyticsEngine({}, bus)
    
    with pytest.raises(AnalyticsInitializationError):
        engine.analyze(1, "e1", {})
        
    engine.initialize()
    record = engine.analyze(1, "e1", {})
    assert record.round_id == 1
    assert record.experiment_id == "e1"

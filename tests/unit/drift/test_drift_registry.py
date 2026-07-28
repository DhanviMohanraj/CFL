"""Tests for Drift History and Registry.

Author: DriftAdapt Contributors
"""

from app.drift.drift_schema import DriftReport
from app.drift.drift_registry import DriftRegistry
from app.drift.drift_history import DriftHistory


def test_drift_registry():
    registry = DriftRegistry()
    report = DriftReport(clinic_id="c1", month=1, baseline_month=0)
    registry.register(report)
    
    assert registry.lookup("c1", 1) is not None
    assert registry.lookup("c2", 1) is None
    assert registry.statistics()["total_reports"] == 1


def test_drift_history():
    history = DriftHistory()
    report = DriftReport(clinic_id="c1", month=1, baseline_month=0)
    history.record_report(report)
    
    assert len(history.get_history()) == 1
    assert len(history.get_clinic_history("c1")) == 1

"""Tests for Policies.

Author: DriftAdapt Contributors
"""

from app.drift.drift_schema import DriftReport
from app.adaptation.policies.no_adaptation import NoAdaptationPolicy
from app.adaptation.policies.local_policy import LocalPolicy
from app.adaptation.policies.multi_clinic_policy import MultiClinicPolicy
from app.adaptation.policies.global_policy import GlobalPolicy
from app.adaptation.policies.emergency_policy import EmergencyPolicy
from app.adaptation.policies.progressive_policy import ProgressivePolicy
from app.adaptation.policies.deferred_policy import DeferredPolicy


def test_no_adaptation_policy():
    policy = NoAdaptationPolicy()
    assert policy.is_applicable([], {})
    
    report = DriftReport(clinic_id="c1", month=1, baseline_month=0, drift_detected=False)
    assert policy.evaluate([report], {}) == 1.0


def test_local_policy():
    policy = LocalPolicy()
    report = DriftReport(clinic_id="c1", month=1, baseline_month=0, drift_detected=True)
    assert policy.is_applicable([report], {})
    assert policy.evaluate([report], {}) == 0.9


def test_multi_clinic_policy():
    policy = MultiClinicPolicy()
    r1 = DriftReport(clinic_id="c1", month=1, baseline_month=0, drift_detected=True)
    r2 = DriftReport(clinic_id="c2", month=1, baseline_month=0, drift_detected=True)
    r3 = DriftReport(clinic_id="c3", month=1, baseline_month=0, drift_detected=False)
    
    assert policy.is_applicable([r1, r2, r3], {})
    assert policy.evaluate([r1, r2, r3], {}) == 0.8


def test_global_policy():
    policy = GlobalPolicy()
    r1 = DriftReport(clinic_id="c1", month=1, baseline_month=0, drift_detected=True)
    r2 = DriftReport(clinic_id="c2", month=1, baseline_month=0, drift_detected=True)
    r3 = DriftReport(clinic_id="c3", month=1, baseline_month=0, drift_detected=True)
    
    assert policy.is_applicable([r1, r2, r3], {"global_clinic_threshold": 3})
    assert policy.evaluate([r1, r2, r3], {}) == 1.0


def test_emergency_policy():
    import pytest
    policy = EmergencyPolicy()
    r1 = DriftReport(clinic_id="c1", month=1, baseline_month=0, drift_detected=True, severity="SIGNIFICANT")
    assert policy.is_applicable([r1], {})
    assert policy.evaluate([r1], {}) == pytest.approx(0.8)


def test_progressive_policy():
    policy = ProgressivePolicy()
    r1 = DriftReport(clinic_id="c1", month=1, baseline_month=0, drift_detected=True, severity="MODERATE")
    assert policy.is_applicable([r1], {})
    assert policy.evaluate([r1], {}) == 0.75


def test_deferred_policy():
    policy = DeferredPolicy()
    r1 = DriftReport(clinic_id="c1", month=1, baseline_month=0, drift_detected=True, severity="LOW")
    assert policy.is_applicable([r1], {})
    assert policy.evaluate([r1], {}) == 0.8

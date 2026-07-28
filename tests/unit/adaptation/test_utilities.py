"""Tests for Adaptation Utilities.

Author: DriftAdapt Contributors
"""

from app.drift.drift_schema import DriftReport
from app.adaptation.utilities.priority_calculator import PriorityCalculator
from app.adaptation.utilities.severity_mapper import SeverityMapper
from app.adaptation.utilities.clinic_selector import ClinicSelector


def test_priority_calculator():
    r1 = DriftReport(clinic_id="c1", month=1, baseline_month=0, severity="SIGNIFICANT")
    r2 = DriftReport(clinic_id="c2", month=1, baseline_month=0, severity="MODERATE")
    r3 = DriftReport(clinic_id="c3", month=1, baseline_month=0, severity="LOW")
    
    assert PriorityCalculator.calculate([r1], {}) == "HIGH"
    assert PriorityCalculator.calculate([r2], {}) == "MEDIUM"
    assert PriorityCalculator.calculate([r3], {}) == "LOW"
    assert PriorityCalculator.calculate([r1, r1, r1], {"global_clinic_threshold": 3}) == "CRITICAL"


def test_severity_mapper():
    assert SeverityMapper.map_severity(0.05, 0.1) == "NONE"
    assert SeverityMapper.map_severity(0.12, 0.1) == "LOW"
    assert SeverityMapper.map_severity(0.2, 0.1) == "MODERATE"
    assert SeverityMapper.map_severity(0.3, 0.1) == "SIGNIFICANT"


def test_clinic_selector():
    r1 = DriftReport(clinic_id="c1", month=1, baseline_month=0, drift_detected=True, severity="SIGNIFICANT")
    r2 = DriftReport(clinic_id="c2", month=1, baseline_month=0, drift_detected=False)
    
    assert ClinicSelector.get_affected_clinics([r1, r2]) == ["c1"]
    assert ClinicSelector.get_severe_clinics([r1, r2]) == ["c1"]

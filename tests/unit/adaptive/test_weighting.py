"""Tests for Adaptive Weighting.

Author: DriftAdapt Contributors
"""

from app.drift.drift_schema import DriftReport
from app.adaptive.weighting.severity_weights import SeverityWeights
from app.adaptive.weighting.clinic_weights import ClinicWeights
from app.adaptive.weighting.historical_weights import HistoricalWeights
from app.adaptive.weighting.confidence_weights import ConfidenceWeights


def test_severity_weights():
    r1 = DriftReport(clinic_id="c1", month=1, baseline_month=0, severity="SIGNIFICANT")
    r2 = DriftReport(clinic_id="c2", month=1, baseline_month=0, severity="MODERATE")
    r3 = DriftReport(clinic_id="c3", month=1, baseline_month=0, severity="LOW")
    
    weights = SeverityWeights.calculate([r1, r2, r3], {})
    assert weights["c1"] == 0.5
    assert weights["c2"] == 0.3
    assert weights["c3"] == 0.2


def test_clinic_weights():
    weights = ClinicWeights.calculate(["c1", "c2"], {})
    assert weights["c1"] == 0.5


def test_historical_weights():
    weights = HistoricalWeights.calculate(["c1", "c2"], {})
    assert weights["c1"] == 0.5


def test_confidence_weights():
    weights = ConfidenceWeights.calculate(["c1", "c2"], 0.9, {})
    assert weights["c1"] == 0.5

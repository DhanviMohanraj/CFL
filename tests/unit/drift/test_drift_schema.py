"""Tests for Drift Schema and Exceptions.

Author: DriftAdapt Contributors
"""

from app.drift.drift_schema import DriftReport, FeatureDriftScore
from app.drift.drift_exceptions import DriftError


def test_drift_schema():
    score = FeatureDriftScore(
        feature_name="age",
        detector="PSI",
        score=0.3,
        is_drift=True,
        threshold=0.25
    )
    assert score.is_drift is True
    
    report = DriftReport(
        clinic_id="c1",
        month=2,
        baseline_month=1,
        feature_scores=[score],
        drift_detected=True,
        drift_type="COVARIATE",
        severity="MODERATE"
    )
    
    assert report.clinic_id == "c1"
    assert report.drift_detected is True

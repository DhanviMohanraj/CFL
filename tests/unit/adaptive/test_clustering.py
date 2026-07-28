"""Tests for Adaptive Clustering.

Author: DriftAdapt Contributors
"""

from app.drift.drift_schema import DriftReport
from app.adaptive.clustering.drift_cluster import DriftCluster


def test_drift_cluster():
    r1 = DriftReport(clinic_id="c1", month=1, baseline_month=0, severity="SIGNIFICANT")
    r2 = DriftReport(clinic_id="c2", month=1, baseline_month=0, severity="MODERATE")
    r3 = DriftReport(clinic_id="c3", month=1, baseline_month=0, drift_detected=True, severity="LOW")
    r4 = DriftReport(clinic_id="c4", month=1, baseline_month=0, drift_detected=False)
    
    clusters = DriftCluster.cluster([r1, r2, r3, r4], {})
    
    assert "c1" in clusters["severe"]
    assert "c2" in clusters["moderate"]
    assert "c3" in clusters["low"]
    assert "c4" in clusters["none"]

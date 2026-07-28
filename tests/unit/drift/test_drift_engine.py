"""Tests for Drift Engine and Managers.

Author: DriftAdapt Contributors
"""

import pandas as pd
import pytest
from app.core.metrics.metrics_bus import MetricsBus
from app.drift.drift_engine import DriftEngine
from app.drift.analyzers.psi_detector import PSIDetector
from app.drift.drift_exceptions import DriftInitializationError


def test_drift_engine():
    bus = MetricsBus()
    config = {"psi_threshold": 0.1}
    detectors = [PSIDetector()]
    
    engine = DriftEngine(config, bus, detectors)
    
    ref = pd.DataFrame({"f1": [1, 2, 3, 4, 5]})
    cur = pd.DataFrame({"f1": [10, 20, 30, 40, 50]})
    
    with pytest.raises(DriftInitializationError):
        engine.detect("c1", 2, 1, ref, cur)
        
    engine.initialize()
    report = engine.detect("c1", 2, 1, ref, cur)
    
    assert report.drift_detected is True
    assert report.severity == "MODERATE"
    assert report.drift_type == "COVARIATE"

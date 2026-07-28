"""Tests for Drift Analyzers.

Author: DriftAdapt Contributors
"""

import pandas as pd
import numpy as np
from app.drift.analyzers.psi_detector import PSIDetector
from app.drift.analyzers.kl_detector import KLDetector
from app.drift.analyzers.js_detector import JSDetector
from app.drift.analyzers.chi_square_detector import ChiSquareDetector
from app.drift.analyzers.wasserstein_detector import WassersteinDetector


def test_psi_detector():
    ref = pd.DataFrame({"f1": np.random.normal(0, 1, 1000)})
    cur = pd.DataFrame({"f1": np.random.normal(2, 1, 1000)}) # drifted
    
    detector = PSIDetector()
    scores = detector.detect(ref, cur, {"psi_threshold": 0.1})
    
    assert len(scores) == 1
    assert scores[0].is_drift is True


def test_kl_detector():
    ref = pd.DataFrame({"f1": np.random.normal(0, 1, 1000)})
    cur = pd.DataFrame({"f1": np.random.normal(2, 1, 1000)})
    
    detector = KLDetector()
    scores = detector.detect(ref, cur, {"kl_threshold": 0.1})
    assert len(scores) == 1
    assert scores[0].is_drift is True


def test_js_detector():
    ref = pd.DataFrame({"f1": np.random.normal(0, 1, 1000)})
    cur = pd.DataFrame({"f1": np.random.normal(2, 1, 1000)})
    
    detector = JSDetector()
    scores = detector.detect(ref, cur, {"js_threshold": 0.1})
    assert len(scores) == 1
    assert scores[0].is_drift is True


def test_chi_square_detector():
    ref = pd.DataFrame({"cat": ["A"] * 800 + ["B"] * 200})
    cur = pd.DataFrame({"cat": ["A"] * 200 + ["B"] * 800})
    
    detector = ChiSquareDetector()
    scores = detector.detect(ref, cur, {"chi_square_alpha": 0.05})
    assert len(scores) == 1
    assert scores[0].is_drift is True


def test_wasserstein_detector():
    ref = pd.DataFrame({"f1": np.random.normal(0, 1, 1000)})
    cur = pd.DataFrame({"f1": np.random.normal(2, 1, 1000)})
    
    detector = WassersteinDetector()
    scores = detector.detect(ref, cur, {"wasserstein_threshold": 0.1})
    assert len(scores) == 1
    assert scores[0].is_drift is True

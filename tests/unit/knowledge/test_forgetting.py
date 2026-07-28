"""Tests for Forgetting.

Author: DriftAdapt Contributors
"""

from app.knowledge.forgetting.forgetting_detector import ForgettingDetector


def test_forgetting_detector():
    score = ForgettingDetector.detect(None, None, {})
    assert 0.0 <= score <= 1.0

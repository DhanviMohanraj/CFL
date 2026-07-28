"""Tests for Explainability.

Author: DriftAdapt Contributors
"""

from app.analytics.explainability.explanation_engine import ExplanationEngine


def test_explanation_engine():
    engine = ExplanationEngine()
    assert engine is not None

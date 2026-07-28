"""Tests for Utilities.

Author: DriftAdapt Contributors
"""

from app.evaluation.utilities.statistical_summary import StatisticalSummary


def test_statistical_summary():
    summary = StatisticalSummary()
    assert summary is not None

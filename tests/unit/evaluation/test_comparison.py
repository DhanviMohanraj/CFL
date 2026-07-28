"""Tests for Comparison.

Author: DriftAdapt Contributors
"""

from app.evaluation.comparison.baseline_comparator import BaselineComparator


def test_baseline_comparator():
    comparator = BaselineComparator()
    assert comparator is not None

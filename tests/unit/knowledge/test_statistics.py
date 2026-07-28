"""Tests for Statistics.

Author: DriftAdapt Contributors
"""

from app.knowledge.statistics.welford_statistics import WelfordStatistics


def test_welford_statistics():
    stats = WelfordStatistics()
    stats.update(1.0)
    stats.update(3.0)
    stats.update(5.0)
    
    assert stats.mean == 3.0
    assert stats.variance() == 4.0

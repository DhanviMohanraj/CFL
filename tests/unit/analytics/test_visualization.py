"""Tests for Visualization.

Author: DriftAdapt Contributors
"""

from app.analytics.visualization.drift_plot import DriftPlot


def test_drift_plot():
    plot = DriftPlot()
    assert plot is not None

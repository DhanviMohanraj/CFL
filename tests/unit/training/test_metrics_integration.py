"""Tests for Metrics Integration.

Author: DriftAdapt Contributors
"""

from app.training.experiment_metrics import ExperimentMetrics
from app.core.metrics.metrics_bus import MetricsBus


def test_experiment_metrics():
    bus = MetricsBus()
    metrics = ExperimentMetrics(bus)
    
    # Should not raise any errors, as it attempts to publish mock metrics
    metrics.publish_event("experiment.started")
    metrics.publish_value("experiment.duration", 100.0)

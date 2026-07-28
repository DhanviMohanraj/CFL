"""Tests for Execution Metrics.

Author: DriftAdapt Contributors
"""

from app.core.metrics.metrics_bus import MetricsBus
from app.federated.round_execution.execution_metrics import ExecutionMetrics


def test_execution_metrics():
    bus = MetricsBus()
    metrics = ExecutionMetrics(bus)
    
    metrics.publish_event("round.started")
    metrics.publish_value("round.duration", 100.5)

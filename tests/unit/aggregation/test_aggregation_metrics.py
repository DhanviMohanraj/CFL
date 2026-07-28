"""Tests for Aggregation Logger and Metrics.

Author: DriftAdapt Contributors
"""

from app.core.metrics.metrics_bus import MetricsBus
from app.aggregation.aggregation_metrics import AggregationMetrics
from app.aggregation.aggregation_logger import AggregationLogger


def test_aggregation_metrics():
    bus = MetricsBus()
    metrics = AggregationMetrics(bus)
    
    metrics.publish_event("aggregation.started")
    metrics.publish_value("aggregation.duration", 10.0)


def test_aggregation_logger():
    logger = AggregationLogger("r1")
    logger.info("test")

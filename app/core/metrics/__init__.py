"""DriftAdapt Metrics Subpackage.

Author: DriftAdapt Contributors
Purpose: Exposes MetricsBus, Metric model, MetricType, exceptions, and aggregations.
Future Integration: Referenced by all client training nodes and evaluation systems.
"""

from app.core.metrics.metrics_bus import MetricsBus
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType
from app.core.metrics.exceptions import (
    MetricError,
    MetricValidationError,
    MetricAlreadyExists,
    MetricNotFound,
    ExportError,
    LoggerInitializationError,
)
from app.core.metrics.exporters import CSVMetricExporter, JSONMetricExporter
from app.core.metrics.aggregation import (
    aggregate_mean,
    aggregate_max,
    aggregate_min,
    aggregate_median,
    aggregate_variance,
    aggregate_stddev,
    aggregate_latest,
    aggregate_running_average,
    aggregate_grouped,
)
from app.core.metrics.metric_events import (
    MetricEvent,
    MetricPublished,
    MetricUpdated,
    MetricRemoved,
    ExperimentStarted,
    ExperimentFinished,
)
from app.core.metrics.publishers import MetricPublisher
from app.core.metrics.subscribers import MetricSubscriber

__all__ = [
    "MetricsBus",
    "Metric",
    "MetricType",
    "MetricError",
    "MetricValidationError",
    "MetricAlreadyExists",
    "MetricNotFound",
    "ExportError",
    "LoggerInitializationError",
    "CSVMetricExporter",
    "JSONMetricExporter",
    "aggregate_mean",
    "aggregate_max",
    "aggregate_min",
    "aggregate_median",
    "aggregate_variance",
    "aggregate_stddev",
    "aggregate_latest",
    "aggregate_running_average",
    "aggregate_grouped",
    "MetricEvent",
    "MetricPublished",
    "MetricUpdated",
    "MetricRemoved",
    "ExperimentStarted",
    "ExperimentFinished",
    "MetricPublisher",
    "MetricSubscriber",
]

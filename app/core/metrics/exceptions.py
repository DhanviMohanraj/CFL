"""DriftAdapt Metrics Exceptions Module.

Author: DriftAdapt Contributors
Purpose: Defines custom exception classes for the metrics validation, storage, and publishing pipelines.
Future Integration: Raised by MetricsBus, registry, store, and exporters.
"""


class MetricError(Exception):
    """Base exception for all metrics-related issues in DriftAdapt."""

    pass


class MetricValidationError(MetricError):
    """Raised when a metric schema validation fails."""

    pass


class MetricAlreadyExists(MetricError):
    """Raised when attempting to register or publish a duplicate metric structure."""

    pass


class MetricNotFound(MetricError):
    """Raised when a queried metric cannot be located in the registry or store."""

    pass


class ExportError(MetricError):
    """Raised when an exporter fails to serialize or write metrics to disk."""

    pass


class LoggerInitializationError(MetricError):
    """Raised if the LoggerFactory failed to set up before logging metrics."""

    pass

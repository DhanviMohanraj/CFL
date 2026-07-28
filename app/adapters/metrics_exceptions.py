"""DriftAdapt Adapter Metrics Engine Exceptions.

Author: DriftAdapt Contributors
Purpose: Custom structured exceptions for the metrics accounting engine.
"""


class MetricCollectionFailed(Exception):
    """Raised when failing to collect metrics from subsystems."""
    pass


class MetricValidationFailed(Exception):
    """Raised when metrics contain invalid or impossible values."""
    pass


class ExportFailed(Exception):
    """Raised when failing to export metrics to disk."""
    pass


class CommunicationEstimationError(Exception):
    """Raised when communication payload math or bandwidth calculations fail."""
    pass


class StorageMetricsError(Exception):
    """Raised when computing storage metrics fails."""
    pass


class PerformanceMetricsError(Exception):
    """Raised when recording performance metrics fails."""
    pass

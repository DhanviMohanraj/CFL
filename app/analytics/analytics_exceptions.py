"""DriftAdapt Analytics Exceptions.

Author: DriftAdapt Contributors
"""


class AnalyticsError(Exception):
    """Base exception for all analytics errors."""
    pass


class AnalyticsInitializationError(AnalyticsError):
    """Raised when engine initialization fails."""
    pass


class MonitoringError(AnalyticsError):
    """Raised when monitoring fails."""
    pass


class DashboardGenerationError(AnalyticsError):
    """Raised when dashboard generation fails."""
    pass


class VisualizationError(AnalyticsError):
    """Raised when visualization fails."""
    pass


class ReportGenerationError(AnalyticsError):
    """Raised when report generation fails."""
    pass


class ExportError(AnalyticsError):
    """Raised when exporting reports/dashboards fails."""
    pass


class RegistryError(AnalyticsError):
    """Raised when registry operations fail."""
    pass

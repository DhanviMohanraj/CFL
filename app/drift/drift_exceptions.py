"""DriftAdapt Drift Exceptions.

Author: DriftAdapt Contributors
"""


class DriftError(Exception):
    """Base exception for all drift engine errors."""
    pass


class DriftInitializationError(DriftError):
    """Raised when the drift engine fails to initialize."""
    pass


class DatasetComparisonError(DriftError):
    """Raised when comparing datasets fails."""
    pass


class DistributionError(DriftError):
    """Raised when statistical distributions cannot be built or compared."""
    pass


class DetectorExecutionError(DriftError):
    """Raised when a specific drift detector fails."""
    pass


class ThresholdError(DriftError):
    """Raised when threshold configurations are invalid."""
    pass


class ReportGenerationError(DriftError):
    """Raised when report generation fails."""
    pass


class RegistryError(DriftError):
    """Raised when registry operations fail."""
    pass


class HistoryError(DriftError):
    """Raised when history persistence operations fail."""
    pass

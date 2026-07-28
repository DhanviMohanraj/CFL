"""DriftAdapt Adaptive Exceptions.

Author: DriftAdapt Contributors
"""


class AdaptiveError(Exception):
    """Base exception for all adaptive engine errors."""
    pass


class AdaptiveExecutionError(AdaptiveError):
    """Raised when adaptive execution fails."""
    pass


class StrategySelectionError(AdaptiveError):
    """Raised when strategy selection fails."""
    pass


class WeightCalculationError(AdaptiveError):
    """Raised when weight calculation fails."""
    pass


class ClinicClusteringError(AdaptiveError):
    """Raised when clinic clustering fails."""
    pass


class AggregationFailure(AdaptiveError):
    """Raised when adaptive aggregation fails."""
    pass


class RedistributionFailure(AdaptiveError):
    """Raised when adapter redistribution fails."""
    pass


class EffectivenessTrackingError(AdaptiveError):
    """Raised when tracking adaptation effectiveness fails."""
    pass


class RegistryError(AdaptiveError):
    """Raised when registry operations fail."""
    pass


class ValidationError(AdaptiveError):
    """Raised when validation fails."""
    pass


class AdaptiveInitializationError(AdaptiveError):
    """Raised when engine initialization fails."""
    pass

"""DriftAdapt Adaptation Exceptions.

Author: DriftAdapt Contributors
"""


class AdaptationError(Exception):
    """Base exception for all adaptation engine errors."""
    pass


class AdaptationInitializationError(AdaptationError):
    """Raised when the adaptation engine fails to initialize."""
    pass


class PolicyEvaluationError(AdaptationError):
    """Raised when policy evaluation fails."""
    pass


class DecisionGenerationError(AdaptationError):
    """Raised when decision generation fails."""
    pass


class PriorityCalculationError(AdaptationError):
    """Raised when priority calculation fails."""
    pass


class SchedulerError(AdaptationError):
    """Raised when the adaptation scheduler fails."""
    pass


class RegistryError(AdaptationError):
    """Raised when registry operations fail."""
    pass


class ValidationError(AdaptationError):
    """Raised when validation of inputs or decisions fails."""
    pass


class HistoryError(AdaptationError):
    """Raised when history persistence operations fail."""
    pass

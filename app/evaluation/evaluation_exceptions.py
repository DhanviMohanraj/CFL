"""DriftAdapt Evaluation Exceptions.

Author: DriftAdapt Contributors
"""


class EvaluationError(Exception):
    """Base exception for all evaluation errors."""
    pass


class BenchmarkExecutionError(EvaluationError):
    """Raised when benchmark execution fails."""
    pass


class ComparisonError(EvaluationError):
    """Raised when algorithm comparison fails."""
    pass


class StatisticalAnalysisError(EvaluationError):
    """Raised when statistical analysis fails."""
    pass


class AblationError(EvaluationError):
    """Raised when ablation study fails."""
    pass


class PublicationGenerationError(EvaluationError):
    """Raised when publication artifact generation fails."""
    pass


class ReproducibilityError(EvaluationError):
    """Raised when saving reproducibility manifests fails."""
    pass


class RegistryError(EvaluationError):
    """Raised when registry operations fail."""
    pass

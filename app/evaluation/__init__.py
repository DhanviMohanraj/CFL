"""DriftAdapt Evaluation Module.

Author: DriftAdapt Contributors
"""

from app.evaluation.evaluation_exceptions import (
    EvaluationError,
    BenchmarkExecutionError,
    ComparisonError,
    StatisticalAnalysisError,
    AblationError,
    PublicationGenerationError,
    ReproducibilityError,
    RegistryError
)
from app.evaluation.evaluation_schema import EvaluationRecord
from app.evaluation.benchmark_registry import BenchmarkRegistry
from app.evaluation.benchmark_history import BenchmarkHistory
from app.evaluation.benchmark_validator import BenchmarkValidator
from app.evaluation.benchmark_manager import BenchmarkManager
from app.evaluation.evaluation_manager import EvaluationManager
from app.evaluation.evaluation_engine import EvaluationEngine
# from app.evaluation.evaluation_logger import EvaluationLogger
# from app.evaluation.evaluation_metrics import EvaluationMetrics

__all__ = [
    "EvaluationError",
    "BenchmarkExecutionError",
    "ComparisonError",
    "StatisticalAnalysisError",
    "AblationError",
    "PublicationGenerationError",
    "ReproducibilityError",
    "RegistryError",
    "EvaluationRecord",
    "BenchmarkRegistry",
    "BenchmarkHistory",
    "BenchmarkValidator",
    "BenchmarkManager",
    "EvaluationManager",
    "EvaluationEngine",
]

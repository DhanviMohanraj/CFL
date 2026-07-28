"""DriftAdapt Aggregation Module.

Author: DriftAdapt Contributors
"""

from app.aggregation.aggregation_exceptions import (
    AggregationError,
    AggregationInitializationError,
    AlgorithmSelectionError,
    AdapterCompatibilityError,
    TensorShapeError,
    WeightedAggregationError,
    FedProxExecutionError,
    ValidationFailure,
    AggregationExportError,
    RegistryError
)
from app.aggregation.aggregation_schema import AggregationMetadata
from app.aggregation.aggregation_context import AggregationContext
from app.aggregation.aggregation_metrics import AggregationMetrics
from app.aggregation.aggregation_logger import AggregationLogger
from app.aggregation.aggregation_history import AggregationHistory
from app.aggregation.aggregation_registry import AggregationRegistry
from app.aggregation.aggregation_validator import AggregationValidator

__all__ = [
    "AggregationError",
    "AggregationInitializationError",
    "AlgorithmSelectionError",
    "AdapterCompatibilityError",
    "TensorShapeError",
    "WeightedAggregationError",
    "FedProxExecutionError",
    "ValidationFailure",
    "AggregationExportError",
    "RegistryError",
    "AggregationMetadata",
    "AggregationContext",
    "AggregationMetrics",
    "AggregationLogger",
    "AggregationHistory",
    "AggregationRegistry",
    "AggregationValidator",
]

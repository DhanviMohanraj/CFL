"""DriftAdapt Adaptive Module.

Author: DriftAdapt Contributors
"""

from app.adaptive.adaptive_exceptions import (
    AdaptiveError,
    AdaptiveExecutionError,
    StrategySelectionError,
    WeightCalculationError,
    ClinicClusteringError,
    AggregationFailure,
    RedistributionFailure,
    EffectivenessTrackingError,
    RegistryError,
    ValidationError,
    AdaptiveInitializationError
)
from app.adaptive.adaptive_schema import AdaptiveRecord
from app.adaptive.adaptive_registry import AdaptiveRegistry
from app.adaptive.adaptive_logger import AdaptiveLogger
from app.adaptive.adaptive_metrics import AdaptiveMetrics
from app.adaptive.adaptive_history import AdaptiveHistory
from app.adaptive.adaptive_validator import AdaptiveValidator
from app.adaptive.adaptive_manager import AdaptiveManager
from app.adaptive.adaptive_engine import AdaptiveFederationEngine

__all__ = [
    "AdaptiveError",
    "AdaptiveExecutionError",
    "StrategySelectionError",
    "WeightCalculationError",
    "ClinicClusteringError",
    "AggregationFailure",
    "RedistributionFailure",
    "EffectivenessTrackingError",
    "RegistryError",
    "ValidationError",
    "AdaptiveInitializationError",
    "AdaptiveRecord",
    "AdaptiveRegistry",
    "AdaptiveLogger",
    "AdaptiveMetrics",
    "AdaptiveHistory",
    "AdaptiveValidator",
    "AdaptiveManager",
    "AdaptiveFederationEngine"
]

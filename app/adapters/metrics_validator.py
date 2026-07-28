"""DriftAdapt Metrics Validator.

Author: DriftAdapt Contributors
Purpose: Validates structural integrity and physical plausibility of metrics.
"""

from typing import Any, Dict, Set

from app.adapters.metrics_exceptions import MetricValidationFailed
from app.core.logging.logger_factory import LoggerFactory


class MetricsValidator:
    """Validates metrics data."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("MetricsValidator")
        
    def validate_numeric(self, value: float, name: str, allow_negative: bool = False) -> None:
        """Validates that a numeric value is plausible."""
        if not allow_negative and value < 0:
            raise MetricValidationFailed(f"Metric '{name}' cannot be negative. Got {value}.")
            
    def validate_timestamp(self, ts: float) -> None:
        """Validates timestamp."""
        if ts <= 0:
            raise MetricValidationFailed("Timestamp must be strictly positive.")
            
    def validate_unique(self, current_ids: Set[str], new_id: str) -> None:
        """Validates ID uniqueness."""
        if new_id in current_ids:
            raise MetricValidationFailed(f"Duplicate metric ID detected: {new_id}")

"""DriftAdapt Metric Registry Module.

Author: DriftAdapt Contributors
Purpose: Validates, catalogs, and stores descriptions and types of registered metrics.
Future Integration: Invoked by publishers prior to writing to memory or files.
"""

import threading
from typing import Any, Dict, Optional

from app.core.metrics.exceptions import MetricAlreadyExists, MetricNotFound, MetricValidationError
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType


class MetricSchema:
    """Represents cataloged metadata of a metric."""

    def __init__(
        self,
        name: str,
        category: MetricType,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self.category = category
        self.description = description
        self.metadata = metadata or {}


class MetricRegistry:
    """Catalog managing schema types and semantic descriptions of metrics.

    This registry is thread-safe.
    """

    def __init__(self) -> None:
        self._schemas: Dict[str, MetricSchema] = {}
        self._lock = threading.Lock()

    def register_schema(
        self,
        name: str,
        category: MetricType,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Registers a schema definition for a metric.

        Raises:
            MetricAlreadyExists: If a schema under this name is already cataloged.
        """
        with self._lock:
            if name in self._schemas:
                raise MetricAlreadyExists(
                    f"Metric schema under name '{name}' is already registered."
                )

            self._schemas[name] = MetricSchema(
                name=name, category=category, description=description, metadata=metadata
            )

    def get_schema(self, name: str) -> MetricSchema:
        """Retrieves a registered schema definition.

        Raises:
            MetricNotFound: If the requested metric name cannot be found.
        """
        with self._lock:
            if name not in self._schemas:
                raise MetricNotFound(f"Metric schema '{name}' is not registered.")
            return self._schemas[name]

    def is_registered(self, name: str) -> bool:
        """Checks if a schema definition exists for the metric name."""
        with self._lock:
            return name in self._schemas

    def validate_metric(self, metric: Metric) -> None:
        """Validates that a metric conforms to its registered schema.

        If the metric name is not registered, raises MetricValidationError.
        """
        if not self.is_registered(metric.name):
            # Strict mode: raise error, or warning depending on system setup.
            # In production research platforms, we raise ValidationError
            # to guarantee schema consistency.
            raise MetricValidationError(
                f"Metric '{metric.name}' cannot be published because its schema is not registered."
            )

        schema = self.get_schema(metric.name)

        # Category specific bounds validation checks
        if schema.category == MetricType.ACCURACY:
            # Accuracy metric values should be float bounded in range [0.0, 1.0] or [0.0, 100.0]
            if isinstance(metric.value, (int, float)):
                val = float(metric.value)
                if not (0.0 <= val <= 100.0):
                    raise MetricValidationError(
                        f"Accuracy value must reside in bounds [0, 100]. Got: {val}"
                    )
            else:
                raise MetricValidationError(
                    f"Accuracy metrics must be numeric. Got type: {type(metric.value)}"
                )

        elif schema.category == MetricType.LOSS:
            # Loss metric values should be numeric non-negative floats
            if isinstance(metric.value, (int, float)):
                val = float(metric.value)
                if val < 0.0:
                    raise MetricValidationError(
                        f"Loss metric value cannot be negative. Got: {val}"
                    )
            else:
                raise MetricValidationError(
                    f"Loss metrics must be numeric. Got type: {type(metric.value)}"
                )

        elif schema.category in (MetricType.CPU, MetricType.GPU, MetricType.MEMORY):
            # Resource usage must be non-negative numbers
            if isinstance(metric.value, (int, float)):
                val = float(metric.value)
                if val < 0.0:
                    raise MetricValidationError(
                        f"Resource utilization cannot be negative. Got: {val}"
                    )
            else:
                raise MetricValidationError(
                    f"Resource utilization metrics must be numeric. Got type: {type(metric.value)}"
                )

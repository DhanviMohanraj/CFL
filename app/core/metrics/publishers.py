"""DriftAdapt Metric Publisher Interfaces.

Author: DriftAdapt Contributors
Purpose: Declares interfaces for publishing single, asynchronous, or batched metrics.
Future Integration: Inherited by MetricsBus and custom client nodes.
"""

from abc import ABC, abstractmethod
from typing import List

from app.core.metrics.metric import Metric


class MetricPublisher(ABC):
    """Abstract interface defining required behaviors to publish metrics."""

    @abstractmethod
    def publish(self, metric: Metric) -> None:
        """Publishes a single metric synchronously."""
        pass

    @abstractmethod
    def publish_batch(self, metrics: List[Metric]) -> None:
        """Publishes a list of metrics."""
        pass

    @abstractmethod
    def publish_async(self, metric: Metric) -> None:
        """Publishes a single metric asynchronously in a background worker."""
        pass

    @abstractmethod
    def validate_before_publish(self, metric: Metric) -> None:
        """Validates metric structure and categories, raising exceptions on failure."""
        pass

"""DriftAdapt Metric Subscriber Interfaces.

Author: DriftAdapt Contributors
Purpose: Declares base observer subscription hooks for metrics and experiments.
Future Integration: Inherited by Tensorboard, Plotly, Dashboard, and MLflow adapters.
"""

from abc import ABC, abstractmethod

from app.core.metrics.metric_events import MetricEvent


class MetricSubscriber(ABC):
    """Abstract interface defining required behaviors to subscribe to metrics event notifications."""

    @abstractmethod
    def on_event(self, event: MetricEvent) -> None:
        """Invoked when a metric event occurs."""
        pass

"""DriftAdapt Metric Events Module.

Author: DriftAdapt Contributors
Purpose: Observer / Pub-Sub pattern for metric updates and experiment lifecycles.
Future Integration: Subscribed to by visualization engines, exporters, and trackers.
"""

import threading
from typing import Any, Callable, Dict, List, Type

from app.core.metrics.metric import Metric


class MetricEvent:
    """Base class for all events in the metrics pipeline."""

    pass


class MetricPublished(MetricEvent):
    """Fired when a new metric record is successfully validated and published."""

    def __init__(self, metric: Metric) -> None:
        self.metric = metric


class MetricUpdated(MetricEvent):
    """Fired when a metric value is modified or appended."""

    def __init__(self, metric: Metric) -> None:
        self.metric = metric


class MetricRemoved(MetricEvent):
    """Fired when a metric is cleared or removed."""

    def __init__(self, name: str) -> None:
        self.name = name


class ExperimentStarted(MetricEvent):
    """Fired when an experiment run begins."""

    def __init__(self, experiment_id: str) -> None:
        self.experiment_id = experiment_id


class ExperimentFinished(MetricEvent):
    """Fired when an experiment run concludes."""

    def __init__(self, experiment_id: str) -> None:
        self.experiment_id = experiment_id


# Handler signature: callable taking an event instance and returning nothing
EventHandler = Callable[[Any], None]


class EventBus:
    """Thread-safe observer system delivering metric events to subscribers."""

    def __init__(self) -> None:
        self._subscribers: Dict[Type[MetricEvent], List[EventHandler]] = {}
        self._lock = threading.Lock()

    def subscribe(self, event_type: Type[MetricEvent], handler: EventHandler) -> None:
        """Registers an event handler callback for a specific event type."""
        with self._lock:
            self._subscribers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: Type[MetricEvent], handler: EventHandler) -> None:
        """Removes a registered callback handler for an event type."""
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(handler)
                except ValueError:
                    pass

    def notify(self, event: MetricEvent) -> None:
        """Dispatches an event instance to all registered handlers thread-safely."""
        event_type = type(event)
        handlers_to_run = []

        with self._lock:
            if event_type in self._subscribers:
                # Copy list to run handlers outside the lock scope
                handlers_to_run = list(self._subscribers[event_type])

        for handler in handlers_to_run:
            try:
                handler(event)
            except Exception as e:
                # Import logger dynamically to avoid circular references during init
                from loguru import logger
                logger.error(f"Error in EventBus subscriber handler: {e}")

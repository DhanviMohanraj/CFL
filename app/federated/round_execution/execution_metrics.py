"""DriftAdapt Execution Metrics.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, Optional
from app.core.metrics.metrics_bus import MetricsBus
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType


class ExecutionMetrics:
    """Helper class to publish round execution metrics."""
    
    def __init__(self, metrics_bus: MetricsBus) -> None:
        self._bus = metrics_bus
        self._register_schemas()
        
    def _register_schemas(self) -> None:
        schemas = [
            ("round.started", MetricType.SYSTEM, "Round execution started"),
            ("round.completed", MetricType.SYSTEM, "Round execution completed"),
            ("round.failed", MetricType.SYSTEM, "Round execution failed"),
            ("training.dispatched", MetricType.FEDERATION, "Training tasks dispatched to clients"),
            ("training.completed", MetricType.FEDERATION, "Client training completed"),
            ("adapter.received", MetricType.FEDERATION, "Adapter received from client"),
            ("adapter.validated", MetricType.VALIDATION, "Adapter validated"),
            ("aggregation.triggered", MetricType.FEDERATION, "Aggregation triggered"),
            ("aggregation.completed", MetricType.FEDERATION, "Aggregation completed"),
            ("redistribution.started", MetricType.FEDERATION, "Redistribution started"),
            ("redistribution.completed", MetricType.FEDERATION, "Redistribution completed"),
            ("round.duration", MetricType.LATENCY, "Round execution duration"),
            ("client.wait.time", MetricType.LATENCY, "Time spent waiting for clients"),
            ("communication.time", MetricType.LATENCY, "Time spent on communication"),
            ("adapter.validation.time", MetricType.LATENCY, "Time spent validating adapters"),
        ]
        for name, category, desc in schemas:
            try:
                self._bus.register_schema(name, category, desc)
            except Exception:
                pass
                
    def _publish(self, name: str, value: Any, tags: Optional[Dict[str, Any]] = None) -> None:
        metric = Metric(
            name=name,
            value=value,
            module="RoundExecution",
            tags=tags or {}
        )
        self._bus.publish(metric)
        
    def publish_event(self, event_name: str, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(event_name, 1, tags=tags)
        
    def publish_value(self, name: str, value: Any, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(name, value, tags=tags)

"""DriftAdapt Aggregation Metrics.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, Optional
from app.core.metrics.metrics_bus import MetricsBus
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType


class AggregationMetrics:
    """Helper class to publish aggregation metrics."""
    
    def __init__(self, metrics_bus: MetricsBus) -> None:
        self._bus = metrics_bus
        self._register_schemas()
        
    def _register_schemas(self) -> None:
        schemas = [
            ("aggregation.started", MetricType.FEDERATION, "Aggregation started"),
            ("aggregation.completed", MetricType.FEDERATION, "Aggregation completed"),
            ("aggregation.failed", MetricType.FEDERATION, "Aggregation failed"),
            ("aggregation.algorithm", MetricType.FEDERATION, "Algorithm used for aggregation"),
            ("aggregation.duration", MetricType.LATENCY, "Duration of aggregation"),
            ("aggregation.participants", MetricType.FEDERATION, "Number of participating clients"),
            ("aggregation.adapter.count", MetricType.FEDERATION, "Number of adapters aggregated"),
            ("aggregation.validation.time", MetricType.LATENCY, "Time spent validating adapters"),
            ("aggregation.memory", MetricType.SYSTEM, "Memory used during aggregation"),
            ("aggregation.output.version", MetricType.FEDERATION, "Version of the output global adapter"),
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
            module="Aggregation",
            tags=tags or {}
        )
        self._bus.publish(metric)
        
    def publish_event(self, event_name: str, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(event_name, 1, tags=tags)
        
    def publish_value(self, name: str, value: Any, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(name, value, tags=tags)

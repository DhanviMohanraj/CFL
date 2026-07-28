"""DriftAdapt Adaptive Metrics.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, Optional
from app.core.metrics.metrics_bus import MetricsBus
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType


class AdaptiveMetrics:
    """Helper class to publish adaptive aggregation metrics."""
    
    def __init__(self, metrics_bus: MetricsBus) -> None:
        self._bus = metrics_bus
        self._register_schemas()
        
    def _register_schemas(self) -> None:
        schemas = [
            ("adaptive.started", MetricType.FEDERATION, "Adaptive aggregation started"),
            ("adaptive.completed", MetricType.FEDERATION, "Adaptive aggregation completed"),
            ("adaptive.failed", MetricType.FEDERATION, "Adaptive aggregation failed"),
            ("adaptive.strategy", MetricType.FEDERATION, "Adaptive strategy selected"),
            ("adaptive.weighting", MetricType.FEDERATION, "Adaptive weighting applied"),
            ("adaptive.cluster.count", MetricType.FEDERATION, "Number of clinics in a cluster"),
            ("adaptive.participation", MetricType.FEDERATION, "Clinic participation count"),
            ("adaptive.redistribution", MetricType.FEDERATION, "Redistribution started"),
            ("adaptive.effectiveness", MetricType.FEDERATION, "Effectiveness score"),
            ("adaptive.execution.time", MetricType.LATENCY, "Time taken for adaptive execution"),
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
            module="AdaptiveEngine",
            tags=tags or {}
        )
        self._bus.publish(metric)
        
    def publish_event(self, event_name: str, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(event_name, 1, tags=tags)
        
    def publish_value(self, name: str, value: Any, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(name, value, tags=tags)

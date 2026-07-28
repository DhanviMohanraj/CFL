"""DriftAdapt Knowledge Consolidation Metrics.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, Optional
from app.core.metrics.metrics_bus import MetricsBus
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType


class ConsolidationMetrics:
    """Helper class to publish knowledge consolidation metrics."""
    
    def __init__(self, metrics_bus: MetricsBus) -> None:
        self._bus = metrics_bus
        self._register_schemas()
        
    def _register_schemas(self) -> None:
        schemas = [
            ("knowledge.consolidation.started", MetricType.SYSTEM, "Consolidation started"),
            ("knowledge.consolidation.completed", MetricType.SYSTEM, "Consolidation completed"),
            ("prototype.updated", MetricType.SYSTEM, "Prototype bank updated"),
            ("forgetting.score", MetricType.SYSTEM, "Forgetting score"),
            ("retention.score", MetricType.SYSTEM, "Knowledge retention score"),
            ("privacy.epsilon", MetricType.SYSTEM, "Privacy budget epsilon"),
            ("privacy.delta", MetricType.SYSTEM, "Privacy budget delta"),
            ("svd.rank", MetricType.SYSTEM, "Truncated SVD rank"),
            ("adapter.reconstructed", MetricType.SYSTEM, "Adapter reconstructed"),
            ("knowledge.stability", MetricType.SYSTEM, "Knowledge stability score"),
            ("consolidation.execution.time", MetricType.LATENCY, "Time taken for consolidation"),
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
            module="KnowledgeEngine",
            tags=tags or {}
        )
        self._bus.publish(metric)
        
    def publish_event(self, event_name: str, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(event_name, 1, tags=tags)
        
    def publish_value(self, name: str, value: Any, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(name, value, tags=tags)

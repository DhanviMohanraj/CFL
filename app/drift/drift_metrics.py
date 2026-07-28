"""DriftAdapt Drift Metrics.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, Optional
from app.core.metrics.metrics_bus import MetricsBus
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType


class DriftMetrics:
    """Helper class to publish drift metrics."""
    
    def __init__(self, metrics_bus: MetricsBus) -> None:
        self._bus = metrics_bus
        self._register_schemas()
        
    def _register_schemas(self) -> None:
        schemas = [
            ("drift.detected", MetricType.DRIFT, "Drift detected"),
            ("drift.none", MetricType.DRIFT, "No drift detected"),
            ("drift.psi", MetricType.DRIFT, "PSI Score"),
            ("drift.kl", MetricType.DRIFT, "KL Divergence"),
            ("drift.js", MetricType.DRIFT, "JS Divergence"),
            ("drift.wasserstein", MetricType.DRIFT, "Wasserstein Distance"),
            ("drift.feature.count", MetricType.DRIFT, "Number of features analyzed"),
            ("drift.severity", MetricType.DRIFT, "Drift severity"),
            ("drift.month", MetricType.SYSTEM, "Analysis month"),
            ("drift.clinic", MetricType.SYSTEM, "Analysis clinic"),
            ("drift.analysis.time", MetricType.LATENCY, "Time taken for drift analysis"),
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
            module="Drift",
            tags=tags or {}
        )
        self._bus.publish(metric)
        
    def publish_event(self, event_name: str, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(event_name, 1, tags=tags)
        
    def publish_value(self, name: str, value: Any, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(name, value, tags=tags)

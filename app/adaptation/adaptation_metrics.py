"""DriftAdapt Adaptation Metrics.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, Optional
from app.core.metrics.metrics_bus import MetricsBus
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType


class AdaptationMetrics:
    """Helper class to publish adaptation metrics."""
    
    def __init__(self, metrics_bus: MetricsBus) -> None:
        self._bus = metrics_bus
        self._register_schemas()
        
    def _register_schemas(self) -> None:
        schemas = [
            ("adaptation.decision.generated", MetricType.SYSTEM, "Adaptation decision generated"),
            ("adaptation.policy.selected", MetricType.SYSTEM, "Policy selected"),
            ("adaptation.priority", MetricType.SYSTEM, "Adaptation priority"),
            ("adaptation.severity", MetricType.SYSTEM, "Drift severity input"),
            ("adaptation.confidence", MetricType.SYSTEM, "Decision confidence"),
            ("adaptation.clinic.count", MetricType.SYSTEM, "Number of clinics requiring adaptation"),
            ("adaptation.global", MetricType.SYSTEM, "Global policy selected"),
            ("adaptation.local", MetricType.SYSTEM, "Local policy selected"),
            ("adaptation.emergency", MetricType.SYSTEM, "Emergency policy selected"),
            ("adaptation.analysis.time", MetricType.LATENCY, "Time taken for decision analysis"),
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
            module="Adaptation",
            tags=tags or {}
        )
        self._bus.publish(metric)
        
    def publish_event(self, event_name: str, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(event_name, 1, tags=tags)
        
    def publish_value(self, name: str, value: Any, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(name, value, tags=tags)

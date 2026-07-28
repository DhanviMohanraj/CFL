"""DriftAdapt Trainer Metrics.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, Optional

from app.core.metrics.metrics_bus import MetricsBus
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType


class TrainerMetrics:
    """Helper class to publish local trainer metrics to the central bus."""
    
    def __init__(self, metrics_bus: MetricsBus) -> None:
        self._bus = metrics_bus
        self._register_schemas()
        
    def _register_schemas(self) -> None:
        schemas = [
            ("training.started", MetricType.TRAINING, "Local training started"),
            ("training.completed", MetricType.TRAINING, "Local training completed"),
            ("training.failed", MetricType.TRAINING, "Local training failed"),
            ("epoch.started", MetricType.TRAINING, "Epoch started"),
            ("epoch.completed", MetricType.TRAINING, "Epoch completed"),
            ("validation.completed", MetricType.VALIDATION, "Validation completed"),
            ("checkpoint.saved", MetricType.SYSTEM, "Checkpoint saved"),
            ("adapter.exported", MetricType.FEDERATION, "Adapter exported"),
            ("training.loss", MetricType.LOSS, "Training loss"),
            ("validation.loss", MetricType.LOSS, "Validation loss"),
            ("training.accuracy", MetricType.VALIDATION, "Training accuracy"),
            ("gpu.memory", MetricType.GPU, "GPU memory usage"),
            ("cpu.memory", MetricType.MEMORY, "CPU memory usage"),
            ("training.duration", MetricType.LATENCY, "Training duration"),
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
            module="LocalTrainer",
            tags=tags or {}
        )
        self._bus.publish(metric)
        
    def publish_event(self, event_name: str, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(event_name, 1, tags=tags)
        
    def publish_value(self, name: str, value: Any, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(name, value, tags=tags)

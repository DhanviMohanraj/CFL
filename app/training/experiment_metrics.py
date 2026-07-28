"""DriftAdapt Experiment Metrics.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, Optional

from app.core.metrics.metrics_bus import MetricsBus
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType


class ExperimentMetrics:
    """Helper class to publish experiment metrics to the central bus."""
    
    def __init__(self, metrics_bus: MetricsBus) -> None:
        self._bus = metrics_bus
        self._register_schemas()
        
    def _register_schemas(self) -> None:
        schemas = [
            ("experiment.started", MetricType.FEDERATION, "Experiment started"),
            ("experiment.completed", MetricType.FEDERATION, "Experiment completed"),
            ("experiment.failed", MetricType.FEDERATION, "Experiment failed"),
            ("experiment.duration", MetricType.LATENCY, "Experiment duration"),
            ("training.round.completed", MetricType.TRAINING, "Training round completed"),
            ("training.month.completed", MetricType.TRAINING, "Training month completed"),
            ("training.clinic.completed", MetricType.TRAINING, "Clinic training completed"),
            ("aggregation.triggered", MetricType.FEDERATION, "Aggregation triggered"),
            ("evaluation.triggered", MetricType.VALIDATION, "Evaluation triggered"),
            ("checkpoint.saved", MetricType.SYSTEM, "Checkpoint saved"),
            ("checkpoint.restored", MetricType.SYSTEM, "Checkpoint restored"),
            ("experiment.progress", MetricType.SYSTEM, "Experiment progress percentage"),
            ("resource.memory", MetricType.MEMORY, "Memory usage"),
            ("resource.cpu", MetricType.CPU, "CPU usage"),
            ("resource.gpu", MetricType.GPU, "GPU usage"),
            ("resource.disk", MetricType.SYSTEM, "Disk usage"),
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
            module="ExperimentManager",
            tags=tags or {}
        )
        self._bus.publish(metric)
        
    def publish_event(self, event_name: str, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(event_name, 1, tags=tags)
        
    def publish_value(self, name: str, value: Any, tags: Optional[Dict[str, Any]] = None) -> None:
        self._publish(name, value, tags=tags)

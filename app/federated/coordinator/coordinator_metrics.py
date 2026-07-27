"""DriftAdapt Coordinator Metrics.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, Optional

from app.core.metrics.metrics_bus import MetricsBus
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType


class CoordinatorMetrics:
    """Helper class to publish coordinator metrics to the central bus."""
    
    def __init__(self, metrics_bus: MetricsBus) -> None:
        self._bus = metrics_bus
        self._register_schemas()
        
    def _register_schemas(self) -> None:
        schemas = [
            ("federation.round.started", MetricType.FEDERATION, "Federated round started"),
            ("federation.active.clients", MetricType.FEDERATION, "Active clients in round"),
            ("federation.round.completed", MetricType.FEDERATION, "Federated round completed"),
            ("federation.round.duration", MetricType.LATENCY, "Federated round duration"),
            ("federation.participation.rate", MetricType.FEDERATION, "Participation rate"),
            ("federation.round.failed", MetricType.FEDERATION, "Federated round failed"),
            ("federation.dropout.rate", MetricType.FEDERATION, "Dropout rate"),
            ("federation.timeout.count", MetricType.FEDERATION, "Federated timeout count"),
            ("federation.retry.count", MetricType.FEDERATION, "Federated retry count"),
            ("federation.upload.wait.time", MetricType.LATENCY, "Upload wait time"),
            ("federation.aggregation.time", MetricType.LATENCY, "Aggregation time"),
            ("federation.distribution.time", MetricType.LATENCY, "Distribution time"),
        ]
        for name, category, desc in schemas:
            try:
                self._bus.register_schema(name, category, desc)
            except Exception:
                pass
                
    def _publish(self, name: str, value: Any, round_num: Optional[int] = None, tags: Optional[Dict[str, Any]] = None) -> None:
        metric = Metric(
            name=name,
            value=value,
            module="FederatedCoordinator",
            round=round_num,
            tags=tags or {}
        )
        self._bus.publish(metric)
        
    def publish_round_started(self, round_num: int, num_clients: int) -> None:
        self._publish("federation.round.started", 1, round_num)
        self._publish("federation.active.clients", num_clients, round_num)
        
    def publish_round_completed(self, round_num: int, duration: float, participation_rate: float) -> None:
        self._publish("federation.round.completed", 1, round_num)
        self._publish("federation.round.duration", duration, round_num)
        self._publish("federation.participation.rate", participation_rate, round_num)
        
    def publish_round_failed(self, round_num: int, reason: str) -> None:
        self._publish("federation.round.failed", 1, round_num, {"reason": reason})
        
    def publish_dropout(self, round_num: int, dropout_rate: float) -> None:
        self._publish("federation.dropout.rate", dropout_rate, round_num)
        
    def publish_timeout(self, event_type: str) -> None:
        self._publish("federation.timeout.count", 1, tags={"type": event_type})
        
    def publish_retry(self, client_id: str) -> None:
        self._publish("federation.retry.count", 1, tags={"client": client_id})
        
    def publish_phase_duration(self, phase: str, duration: float) -> None:
        if phase == "upload":
            self._publish("federation.upload.wait.time", duration)
        elif phase == "aggregation":
            self._publish("federation.aggregation.time", duration)
        elif phase == "distribution":
            self._publish("federation.distribution.time", duration)

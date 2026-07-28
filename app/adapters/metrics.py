"""DriftAdapt Adapter Metrics Publisher.

Author: DriftAdapt Contributors
Purpose: Centralizes metrics publication for adapter state operations to the MetricsBus.
"""

from typing import Any, Optional

from app.core.logging.logger_factory import LoggerFactory
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType
from app.core.metrics.metrics_bus import MetricsBus


class AdapterMetricsPublisher:
    """Thread-safe publisher for adapter state metrics."""

    def __init__(self) -> None:
        """Initializes the publisher and registers schemas."""
        self._bus = MetricsBus()
        self._logger = LoggerFactory.get_logger("AdapterMetricsPublisher")
        self._register_schemas()

    def _register_schemas(self) -> None:
        """Registers metrics schemas specific to adapter state operations."""
        try:
            self._bus.register_schema(
                "adapter_size_bytes", MetricType.PERSONALIZATION, "Adapter payload size in bytes"
            )
            self._bus.register_schema(
                "adapter_size_mb", MetricType.PERSONALIZATION, "Adapter payload size in MB"
            )
            self._bus.register_schema(
                "serialization_time", MetricType.SYSTEM, "Time to serialize adapter in ms"
            )
            self._bus.register_schema(
                "deserialization_time", MetricType.SYSTEM, "Time to deserialize adapter in ms"
            )
            self._bus.register_schema(
                "checksum_time", MetricType.SYSTEM, "Time to compute checksum in ms"
            )
            self._bus.register_schema(
                "parameter_count", MetricType.PERSONALIZATION, "Count of parameters in adapter"
            )
            self._bus.register_schema(
                "communication_payload", MetricType.COMMUNICATION, "Payload size for network"
            )
            self._bus.register_schema(
                "validation_success", MetricType.SYSTEM, "Validation success count"
            )
            self._bus.register_schema(
                "validation_failure", MetricType.SYSTEM, "Validation failure count"
            )
        except Exception as e:
            self._logger.debug(f"Metrics schema registration warning: {e}")

    def publish(self, name: str, value: Any, module: str = "AdapterStateUtilities") -> None:
        """Publishes a metric to the MetricsBus."""
        try:
            metric = Metric(name=name, value=value, module=module)
            self._bus.publish(metric)
        except Exception as e:
            self._logger.warning(f"Failed to publish metric {name}: {e}")

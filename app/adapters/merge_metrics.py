"""DriftAdapt Merge Engine Metrics Publisher.

Author: DriftAdapt Contributors
Purpose: Centralizes metrics publication for adapter merge operations.
"""

from typing import Any

from app.core.logging.logger_factory import LoggerFactory
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType
from app.core.metrics.metrics_bus import MetricsBus


class MergeMetricsPublisher:
    """Thread-safe publisher for merge engine metrics."""

    def __init__(self) -> None:
        self._bus = MetricsBus()
        self._logger = LoggerFactory.get_logger("MergeMetricsPublisher")
        self._register_schemas()

    def _register_schemas(self) -> None:
        try:
            self._bus.register_schema("merge_duration_ms", MetricType.SYSTEM, "Duration of merge in ms")
            self._bus.register_schema("merged_parameter_count", MetricType.PERSONALIZATION, "Output param count")
            self._bus.register_schema("input_adapter_count", MetricType.COMMUNICATION, "Number of merged adapters")
            self._bus.register_schema("communication_payload_bytes", MetricType.COMMUNICATION, "Combined payload size")
            self._bus.register_schema("output_adapter_size", MetricType.PERSONALIZATION, "Size of output adapter")
            self._bus.register_schema("merge_success", MetricType.SYSTEM, "Merge success count")
            self._bus.register_schema("merge_failure", MetricType.SYSTEM, "Merge failure count")
        except Exception as e:
            self._logger.debug(f"Metrics schema registration warning: {e}")

    def publish(self, name: str, value: Any, module: str = "AdapterMergeEngine") -> None:
        try:
            metric = Metric(name=name, value=value, module=module)
            self._bus.publish(metric)
        except Exception as e:
            self._logger.warning(f"Failed to publish metric {name}: {e}")

"""DriftAdapt Metrics Collector.

Author: DriftAdapt Contributors
Purpose: Centralized ingestion point for adapter telemetry.
"""

import threading

from app.adapters.metrics_exceptions import MetricCollectionFailed
from app.adapters.metrics_registry import MetricsRegistry
from app.adapters.metrics_schema import AdapterMetrics, CommunicationMetrics, PerformanceMetrics
from app.adapters.metrics_validator import MetricsValidator
from app.core.logging.logger_factory import LoggerFactory


class MetricsCollector:
    """Ingests, validates, and stores incoming metrics."""
    
    def __init__(self, registry: MetricsRegistry) -> None:
        self._registry = registry
        self._validator = MetricsValidator()
        self._logger = LoggerFactory.get_logger("MetricsCollector")
        self._lock = threading.RLock()
        
    def record_adapter(self, metrics: AdapterMetrics) -> None:
        """Records adapter-specific metrics."""
        with self._lock:
            try:
                self._validator.validate_numeric(metrics.parameter_count, "parameter_count")
                self._validator.validate_numeric(metrics.adapter_size_bytes, "adapter_size_bytes")
                
                history_ids = {m.version_id for m in self._registry.get_adapter_history()}
                self._validator.validate_unique(history_ids, metrics.version_id)
                
                self._registry.add_adapter_metrics(metrics)
                self._logger.debug(f"Recorded adapter metrics for {metrics.version_id}")
            except Exception as e:
                raise MetricCollectionFailed(f"Failed to collect adapter metrics: {e}")
                
    def record_communication(self, metrics: CommunicationMetrics) -> None:
        """Records communication cost estimations."""
        with self._lock:
            try:
                self._validator.validate_numeric(metrics.total_transfer_bytes, "total_transfer_bytes")
                self._registry.add_communication_metrics(metrics)
            except Exception as e:
                raise MetricCollectionFailed(f"Failed to collect communication metrics: {e}")
                
    def record_performance(self, metrics: PerformanceMetrics) -> None:
        """Records system performance overhead metrics."""
        with self._lock:
            try:
                self._validator.validate_numeric(metrics.merge_time_ms, "merge_time_ms")
                self._registry.add_performance_metrics(metrics)
            except Exception as e:
                raise MetricCollectionFailed(f"Failed to collect performance metrics: {e}")
                
    def flush(self) -> None:
        """Forces a flush to persistent storage (if implemented)."""
        pass
        
    def reset(self) -> None:
        """Resets the underlying registry."""
        self._registry.reset()

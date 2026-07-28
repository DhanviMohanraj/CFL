"""DriftAdapt Metrics Registry.

Author: DriftAdapt Contributors
Purpose: Maintains historical metrics in memory.
"""

import threading
from typing import Dict, List

from app.adapters.metrics_schema import AdapterMetrics, CommunicationMetrics, PerformanceMetrics
from app.core.logging.logger_factory import LoggerFactory


class MetricsRegistry:
    """Thread-safe storage for historical metrics."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("MetricsRegistry")
        self._lock = threading.RLock()
        
        # In-memory storage for now. Can be persisted to a database or JSON later.
        self._adapter_metrics: Dict[str, AdapterMetrics] = {}
        self._comm_metrics: List[CommunicationMetrics] = []
        self._perf_metrics: List[PerformanceMetrics] = []
        
    def add_adapter_metrics(self, metrics: AdapterMetrics) -> None:
        with self._lock:
            self._adapter_metrics[metrics.version_id] = metrics
            
    def add_communication_metrics(self, metrics: CommunicationMetrics) -> None:
        with self._lock:
            self._comm_metrics.append(metrics)
            
    def add_performance_metrics(self, metrics: PerformanceMetrics) -> None:
        with self._lock:
            self._perf_metrics.append(metrics)
            
    def get_adapter_history(self) -> List[AdapterMetrics]:
        with self._lock:
            return list(self._adapter_metrics.values())
            
    def get_communication_history(self) -> List[CommunicationMetrics]:
        with self._lock:
            return list(self._comm_metrics)
            
    def get_performance_history(self) -> List[PerformanceMetrics]:
        with self._lock:
            return list(self._perf_metrics)
            
    def get_per_clinic(self, clinic_id: str) -> List[AdapterMetrics]:
        with self._lock:
            return [m for m in self._adapter_metrics.values() if m.clinic_id == clinic_id]
            
    def reset(self) -> None:
        """Clears all stored metrics."""
        with self._lock:
            self._adapter_metrics.clear()
            self._comm_metrics.clear()
            self._perf_metrics.clear()
            self._logger.info("Metrics registry reset.")

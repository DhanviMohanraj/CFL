"""DriftAdapt Performance Metrics.

Author: DriftAdapt Contributors
Purpose: Computes timing and memory overheads for operations.
"""

from app.adapters.metrics_exceptions import PerformanceMetricsError
from app.adapters.metrics_registry import MetricsRegistry


class PerformanceMetricsCalculator:
    """Calculates statistics on performance."""
    
    def __init__(self, registry: MetricsRegistry) -> None:
        self._registry = registry
        
    def average_merge_time(self) -> float:
        """Computes the average merge duration."""
        try:
            history = self._registry.get_performance_history()
            if not history:
                return 0.0
            return sum(m.merge_time_ms for m in history) / len(history)
        except Exception as e:
            raise PerformanceMetricsError(f"Failed to average merge time: {e}")
            
    def average_memory_usage(self) -> float:
        """Computes average memory overhead during operations."""
        try:
            history = self._registry.get_performance_history()
            if not history:
                return 0.0
            return sum(m.memory_usage_mb for m in history) / len(history)
        except Exception as e:
            raise PerformanceMetricsError(f"Failed to average memory: {e}")

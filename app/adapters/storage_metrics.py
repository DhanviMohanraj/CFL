"""DriftAdapt Storage Metrics.

Author: DriftAdapt Contributors
Purpose: Computes storage statistics from the metrics registry.
"""

from typing import Dict

from app.adapters.metrics_exceptions import StorageMetricsError
from app.adapters.metrics_registry import MetricsRegistry


class StorageMetricsCalculator:
    """Computes storage totals, averages, and trends."""
    
    def __init__(self, registry: MetricsRegistry) -> None:
        self._registry = registry
        
    def compute_total_storage_bytes(self) -> int:
        """Returns the total disk space consumed by serialized adapters."""
        try:
            history = self._registry.get_adapter_history()
            return sum(m.serialized_size_bytes for m in history)
        except Exception as e:
            raise StorageMetricsError(f"Failed to compute total storage: {e}")
        
    def compute_storage_per_clinic(self) -> Dict[str, int]:
        """Returns total disk space consumed per clinic."""
        try:
            history = self._registry.get_adapter_history()
            clinic_totals = {}
            for m in history:
                clinic_totals[m.clinic_id] = clinic_totals.get(m.clinic_id, 0) + m.serialized_size_bytes
            return clinic_totals
        except Exception as e:
            raise StorageMetricsError(f"Failed to compute storage per clinic: {e}")
        
    def compute_average_adapter_size(self) -> float:
        """Returns the average size of a serialized adapter."""
        try:
            history = self._registry.get_adapter_history()
            if not history:
                return 0.0
            return sum(m.serialized_size_bytes for m in history) / len(history)
        except Exception as e:
            raise StorageMetricsError(f"Failed to compute average adapter size: {e}")

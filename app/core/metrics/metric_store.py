"""DriftAdapt Metric Store Module.

Author: DriftAdapt Contributors
Purpose: Manages thread-safe in-memory caching and historical querying of metrics.
Future Integration: Invoked by MetricsBus and dashboard publishers to evaluate models.
"""

from typing import List, Dict, Optional, Any
import threading

from app.core.metrics.metric import Metric


class MetricStore:
    """Thread-safe in-memory cache storing all published Metric instances."""

    def __init__(self) -> None:
        self._metrics: List[Metric] = []
        # Cache names to retrieve fast
        self._by_name: Dict[str, List[Metric]] = {}
        self._lock = threading.Lock()

    def append(self, metric: Metric) -> None:
        """Appends a validated metric into memory stores.

        Thread-safe.
        """
        with self._lock:
            self._metrics.append(metric)
            self._by_name.setdefault(metric.name, []).append(metric)

    def retrieve(self, name: str) -> List[Metric]:
        """Retrieves all stored metrics matching the name.

        Returns empty list if none found. Thread-safe.
        """
        with self._lock:
            return list(self._by_name.get(name, []))

    def latest(self, name: str) -> Optional[Metric]:
        """Returns the most recently recorded metric under the name.

        Thread-safe.
        """
        with self._lock:
            metrics_list = self._by_name.get(name)
            if not metrics_list:
                return None
            return metrics_list[-1]

    def history(self, name: str) -> List[Any]:
        """Returns a list of raw values recorded over time for a metric.

        Thread-safe.
        """
        with self._lock:
            metrics_list = self._by_name.get(name)
            if not metrics_list:
                return []
            return [m.value for m in metrics_list]

    def filter(
        self,
        name: Optional[str] = None,
        module: Optional[str] = None,
        client_id: Optional[str] = None,
        experiment_id: Optional[str] = None,
    ) -> List[Metric]:
        """Queries and filters stored metrics based on parameters.

        Thread-safe.
        """
        with self._lock:
            results = self._metrics
            if name:
                results = [m for m in results if m.name == name]
            if module:
                results = [m for m in results if m.module == module]
            if client_id:
                results = [m for m in results if m.client_id == client_id]
            if experiment_id:
                results = [m for m in results if m.experiment_id == experiment_id]
            return list(results)

    def clear(self) -> None:
        """Clears all stored metrics from memory.

        Thread-safe.
        """
        with self._lock:
            self._metrics.clear()
            self._by_name.clear()

"""DriftAdapt Metrics Aggregations Module.

Author: DriftAdapt Contributors
Purpose: Computes statistics (averages, medians, stddev) over lists of Metric objects.
Future Integration: Invoked by clients or aggregators to calculate performance metrics.
"""

import statistics
from typing import List, Dict, Any, Optional
from app.core.metrics.metric import Metric


def _extract_numeric_values(metrics: List[Metric]) -> List[float]:
    """Helper to extract float values from metrics, skipping non-numeric records."""
    numeric = []
    for m in metrics:
        if isinstance(m.value, (int, float)) and not isinstance(m.value, bool):
            numeric.append(float(m.value))
    return numeric


def aggregate_mean(metrics: List[Metric]) -> float:
    """Calculates the arithmetic mean of numeric metric values. Returns 0.0 if empty."""
    vals = _extract_numeric_values(metrics)
    if not vals:
        return 0.0
    return statistics.mean(vals)


def aggregate_max(metrics: List[Metric]) -> float:
    """Calculates the maximum of numeric metric values. Returns 0.0 if empty."""
    vals = _extract_numeric_values(metrics)
    if not vals:
        return 0.0
    return max(vals)


def aggregate_min(metrics: List[Metric]) -> float:
    """Calculates the minimum of numeric metric values. Returns 0.0 if empty."""
    vals = _extract_numeric_values(metrics)
    if not vals:
        return 0.0
    return min(vals)


def aggregate_median(metrics: List[Metric]) -> float:
    """Calculates the median of numeric metric values. Returns 0.0 if empty."""
    vals = _extract_numeric_values(metrics)
    if not vals:
        return 0.0
    return statistics.median(vals)


def aggregate_variance(metrics: List[Metric], sample: bool = True) -> float:
    """Calculates the variance. Returns 0.0 if empty or insufficient values."""
    vals = _extract_numeric_values(metrics)
    if len(vals) < 2:
        return 0.0
    return statistics.variance(vals) if sample else statistics.pvariance(vals)


def aggregate_stddev(metrics: List[Metric], sample: bool = True) -> float:
    """Calculates the standard deviation. Returns 0.0 if empty or insufficient values."""
    vals = _extract_numeric_values(metrics)
    if len(vals) < 2:
        return 0.0
    return statistics.stdev(vals) if sample else statistics.pstdev(vals)


def aggregate_latest(metrics: List[Metric]) -> Optional[Any]:
    """Returns the value of the most recent metric in the list, sorted by timestamp."""
    if not metrics:
        return None
    sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
    return sorted_metrics[-1].value


def aggregate_running_average(metrics: List[Metric]) -> List[float]:
    """Calculates a running average over numeric metrics in order of timestamps."""
    sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
    vals = _extract_numeric_values(sorted_metrics)
    if not vals:
        return []

    running = []
    total = 0.0
    for idx, val in enumerate(vals, start=1):
        total += val
        running.append(total / idx)
    return running


def aggregate_grouped(metrics: List[Metric], group_by: str) -> Dict[Any, List[Metric]]:
    """Groups metrics by a specific metric attribute (e.g. 'client_id', 'module').

    Supported attributes: 'name', 'module', 'step', 'round', 'client_id', 'experiment_id'.
    """
    grouped: Dict[Any, List[Metric]] = {}
    for m in metrics:
        # Retrieve attribute dynamically
        val = getattr(m, group_by, None)
        grouped.setdefault(val, []).append(m)
    return grouped

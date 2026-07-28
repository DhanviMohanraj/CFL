"""DriftAdapt Utilities Module.

Author: DriftAdapt Contributors
"""

from app.aggregation.utilities.tensor_merger import average_tensors, weighted_average_tensors
from app.aggregation.utilities.tensor_validator import check_tensor_compatibility, detect_nans
from app.aggregation.utilities.tensor_statistics import compute_adapter_statistics
from app.aggregation.utilities.compatibility_checker import check_adapters_compatibility
from app.aggregation.utilities.adapter_normalizer import normalize_adapter

__all__ = [
    "average_tensors",
    "weighted_average_tensors",
    "check_tensor_compatibility",
    "detect_nans",
    "compute_adapter_statistics",
    "check_adapters_compatibility",
    "normalize_adapter",
]

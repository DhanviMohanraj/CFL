"""DriftAdapt Tensor Utilities.

Author: DriftAdapt Contributors
"""

import torch
from typing import Dict, List

def check_tensor_compatibility(tensors: List[torch.Tensor]) -> bool:
    if not tensors:
        return True
    shape = tensors[0].shape
    dtype = tensors[0].dtype
    return all(t.shape == shape and t.dtype == dtype for t in tensors)

def detect_nans(state_dict: Dict[str, torch.Tensor]) -> bool:
    for v in state_dict.values():
        if torch.is_floating_point(v) and torch.isnan(v).any():
            return True
    return False

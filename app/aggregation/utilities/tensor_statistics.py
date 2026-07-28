"""DriftAdapt Tensor Statistics.

Author: DriftAdapt Contributors
"""

import torch
from typing import Dict, Any

def compute_adapter_statistics(state_dict: Dict[str, torch.Tensor]) -> Dict[str, Any]:
    """Computes statistics for an adapter state dict."""
    total_params = sum(t.numel() for t in state_dict.values())
    total_memory = sum(t.element_size() * t.numel() for t in state_dict.values())
    num_tensors = len(state_dict)
    
    return {
        "total_parameters": total_params,
        "total_memory_bytes": total_memory,
        "num_tensors": num_tensors
    }

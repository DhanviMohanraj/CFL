"""DriftAdapt Tensor Merger.

Author: DriftAdapt Contributors
"""

import torch
from typing import List

def average_tensors(tensors: List[torch.Tensor]) -> torch.Tensor:
    """Averages a list of tensors."""
    if not tensors:
        raise ValueError("No tensors provided for averaging.")
    stacked = torch.stack(tensors)
    return torch.mean(stacked, dim=0)

def weighted_average_tensors(tensors: List[torch.Tensor], weights: List[float]) -> torch.Tensor:
    """Computes a weighted average of tensors."""
    if len(tensors) != len(weights):
        raise ValueError("Mismatch between number of tensors and weights.")
    if not tensors:
        raise ValueError("No tensors provided for weighted averaging.")
    
    total_weight = sum(weights)
    if total_weight <= 0:
        raise ValueError("Total weight must be positive.")
        
    normalized_weights = [w / total_weight for w in weights]
    weighted_tensors = [t * w for t, w in zip(tensors, normalized_weights)]
    stacked = torch.stack(weighted_tensors)
    return torch.sum(stacked, dim=0)

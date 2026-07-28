"""DriftAdapt Adapter Normalizer.

Author: DriftAdapt Contributors
"""

import torch
from typing import Dict

def normalize_adapter(state_dict: Dict[str, torch.Tensor], epsilon: float = 1e-8) -> Dict[str, torch.Tensor]:
    """Normalizes the tensors in an adapter to have unit norm."""
    normalized = {}
    for k, v in state_dict.items():
        if torch.is_floating_point(v):
            norm = torch.norm(v)
            if norm > epsilon:
                normalized[k] = v / norm
            else:
                normalized[k] = v
        else:
            normalized[k] = v
    return normalized

"""DriftAdapt Compatibility Checker.

Author: DriftAdapt Contributors
"""

from typing import Dict, List, Any
import torch

def check_adapters_compatibility(adapter_state_dicts: List[Dict[str, torch.Tensor]]) -> bool:
    """Checks if a list of adapters are structurally compatible."""
    if not adapter_state_dicts:
        return True
        
    base_keys = set(adapter_state_dicts[0].keys())
    for sd in adapter_state_dicts[1:]:
        if set(sd.keys()) != base_keys:
            return False
            
    return True

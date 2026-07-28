"""DriftAdapt Static FedLoRA Algorithm.

Author: DriftAdapt Contributors
"""

import torch
from typing import Dict, List, Any

from app.aggregation.algorithms.base_algorithm import BaseAlgorithm


class StaticFedLoRA(BaseAlgorithm):
    """Static FedLoRA aggregation algorithm."""
    
    def aggregate(self, adapter_state_dicts: List[Dict[str, torch.Tensor]], metadata: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        if not adapter_state_dicts:
            return {}
            
        global_state_dict = {}
        
        for k in adapter_state_dicts[0].keys():
            tensors = [sd[k] for sd in adapter_state_dicts]
            
            if torch.is_floating_point(tensors[0]):
                stacked = torch.stack(tensors)
                global_state_dict[k] = torch.mean(stacked, dim=0)
            else:
                global_state_dict[k] = tensors[0]
                
        return global_state_dict

"""DriftAdapt FedProx Algorithm.

Author: DriftAdapt Contributors
"""

import torch
from typing import Dict, List, Any

from app.aggregation.algorithms.base_algorithm import BaseAlgorithm


class FedProx(BaseAlgorithm):
    """FedProx aggregation algorithm."""
    
    def aggregate(self, adapter_state_dicts: List[Dict[str, torch.Tensor]], metadata: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        if not adapter_state_dicts:
            return {}
            
        global_state_dict = {}
        
        weights = []
        for meta in metadata:
            weight = meta.get("dataset_size", 1.0)
            weights.append(weight)
            
        total_weight = sum(weights)
        if total_weight <= 0:
            total_weight = len(weights)
            weights = [1.0] * len(weights)
            
        normalized_weights = [w / total_weight for w in weights]
        
        for k in adapter_state_dicts[0].keys():
            tensors = [sd[k] for sd in adapter_state_dicts]
            
            if torch.is_floating_point(tensors[0]):
                weighted_tensors = [t * w for t, w in zip(tensors, normalized_weights)]
                stacked = torch.stack(weighted_tensors)
                global_state_dict[k] = torch.sum(stacked, dim=0)
            else:
                global_state_dict[k] = tensors[0]
                
        return global_state_dict

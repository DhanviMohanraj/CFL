"""DriftAdapt Weighted FedAvg Algorithm.

Author: DriftAdapt Contributors
"""

import torch
from typing import Dict, List, Any

from app.aggregation.algorithms.base_algorithm import BaseAlgorithm
from app.aggregation.aggregation_exceptions import WeightedAggregationError


class WeightedFedAvg(BaseAlgorithm):
    """Federated Averaging weighted by client dataset size."""
    
    def aggregate(self, adapter_state_dicts: List[Dict[str, torch.Tensor]], metadata: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        if not adapter_state_dicts:
            return {}
            
        weights = []
        for meta in metadata:
            weight = meta.get("dataset_size", 1.0)
            weights.append(weight)
            
        total_weight = sum(weights)
        if total_weight <= 0:
            raise WeightedAggregationError("Total weight must be positive.")
            
        normalized_weights = [w / total_weight for w in weights]
        
        global_state_dict = {}
        
        for k in adapter_state_dicts[0].keys():
            tensors = [sd[k] for sd in adapter_state_dicts]
            
            if torch.is_floating_point(tensors[0]):
                weighted_tensors = [t * w for t, w in zip(tensors, normalized_weights)]
                stacked = torch.stack(weighted_tensors)
                global_state_dict[k] = torch.sum(stacked, dim=0)
            else:
                global_state_dict[k] = tensors[0]
                
        return global_state_dict

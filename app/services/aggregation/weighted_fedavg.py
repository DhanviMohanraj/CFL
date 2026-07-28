"""Weighted FedAvg Aggregation Service.

Author: DriftAdapt Contributors
Purpose: Implements Federated Averaging with dynamic weighting based on dataset size or reliability.
"""

from typing import List, Dict, Any, Optional

try:
    import torch
except ImportError:
    pass

from app.core.logging import LoggerFactory
from app.services.aggregation.base_aggregator import BaseAggregator


class WeightedFedAvgService(BaseAggregator):
    """Federated Averaging algorithm utilizing client-specific weights."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("WeightedFedAvgService")
        
    @property
    def algorithm_name(self) -> str:
        return "weighted_fedavg"
        
    def aggregate(
        self,
        state_dicts: List[Dict[str, Any]],
        weights: List[float],
        global_state_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Aggregates state dictionaries using the provided relative weights.
        
        Args:
            state_dicts: List of PyTorch state dictionaries containing LoRA parameters.
            weights: List of floating point weights corresponding to each state dict.
            global_state_dict: Optional global state dict (unused in standard weighted FedAvg).
            
        Returns:
            The weighted average state dictionary.
            
        Raises:
            ValueError: If lengths of state_dicts and weights mismatch, or if keys mismatch.
        """
        if not state_dicts:
            raise ValueError("Cannot aggregate an empty list of state dictionaries.")
            
        if len(state_dicts) != len(weights):
            raise ValueError(f"Mismatched state_dicts ({len(state_dicts)}) and weights ({len(weights)})")
            
        # Normalize weights to ensure they sum to exactly 1.0 (to avoid explosion or decay)
        total_weight = sum(weights)
        if total_weight <= 0:
            raise ValueError("Total weight must be strictly positive.")
            
        normalized_weights = [w / total_weight for w in weights]
        
        self._logger.info(f"Performing Weighted FedAvg across {len(state_dicts)} client updates.")
        
        reference_keys = set(state_dicts[0].keys())
        for sd in state_dicts[1:]:
            if set(sd.keys()) != reference_keys:
                raise ValueError("Mismatch in state dictionary keys across clients.")
                
        averaged_dict: Dict[str, Any] = {}
        
        for key in reference_keys:
            try:
                first_tensor = state_dicts[0][key]
                if not isinstance(first_tensor, torch.Tensor):
                    averaged_dict[key] = first_tensor
                    continue
                    
                dtype = first_tensor.dtype
                if not torch.is_floating_point(first_tensor):
                    averaged_dict[key] = first_tensor
                    continue
                    
                accumulator = torch.zeros_like(first_tensor, dtype=torch.float32)
                
                for sd, weight in zip(state_dicts, normalized_weights):
                    accumulator += (sd[key].to(torch.float32) * weight)
                    
                averaged_dict[key] = accumulator.to(dtype)
                
            except Exception as e:
                self._logger.error(f"Failed to aggregate key {key}", error=str(e))
                raise ValueError(f"Failed to aggregate key {key}: {e}") from e
                
        return averaged_dict

"""FedAvg Aggregation Service.

Author: DriftAdapt Contributors
Purpose: Implements the classical Federated Averaging (FedAvg) algorithm.
"""

from typing import List, Dict, Any, Optional

try:
    import torch
except ImportError:
    pass

from app.core.logging import LoggerFactory
from app.services.aggregation.base_aggregator import BaseAggregator


class FedAvgService(BaseAggregator):
    """Classical Federated Averaging algorithm for LoRA parameters."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("FedAvgService")
        
    @property
    def algorithm_name(self) -> str:
        return "fedavg"
        
    def aggregate(
        self,
        state_dicts: List[Dict[str, Any]],
        weights: List[float],
        global_state_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Aggregates state dictionaries using a simple unweighted or uniform weighted average.
        
        In classical FedAvg, if weights are provided, they are treated as uniform if this
        is strictly the unweighted version, but typically FedAvg handles dataset-size weights.
        We will force equal weighting here to represent standard unweighted averaging.
        For true weighted, use WeightedFedAvg.
        """
        if not state_dicts:
            raise ValueError("Cannot aggregate an empty list of state dictionaries.")
            
        self._logger.info(f"Performing FedAvg across {len(state_dicts)} client updates.")
        
        # Ensure all state dicts have the exact same keys
        reference_keys = set(state_dicts[0].keys())
        for sd in state_dicts[1:]:
            if set(sd.keys()) != reference_keys:
                raise ValueError("Mismatch in state dictionary keys across clients.")
                
        num_clients = len(state_dicts)
        uniform_weight = 1.0 / num_clients
        
        averaged_dict: Dict[str, Any] = {}
        
        for key in reference_keys:
            # We must be careful not to aggregate non-floating point tensors unless necessary,
            # but LoRA parameters are float16/float32.
            try:
                # Initialize with zeros like the first tensor
                first_tensor = state_dicts[0][key]
                if not isinstance(first_tensor, torch.Tensor):
                    # For non-tensors (e.g., ints, strings), we just take the first client's value
                    averaged_dict[key] = first_tensor
                    continue
                    
                # Ensure it's a float for accumulation
                dtype = first_tensor.dtype
                if not torch.is_floating_point(first_tensor):
                    averaged_dict[key] = first_tensor
                    continue
                    
                accumulator = torch.zeros_like(first_tensor, dtype=torch.float32)
                
                for sd in state_dicts:
                    accumulator += (sd[key].to(torch.float32) * uniform_weight)
                    
                # Cast back to original dtype
                averaged_dict[key] = accumulator.to(dtype)
                
            except Exception as e:
                self._logger.error(f"Failed to aggregate key {key}", error=str(e))
                raise ValueError(f"Failed to aggregate key {key}: {e}") from e
                
        return averaged_dict

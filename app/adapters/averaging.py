"""DriftAdapt Naive Averaging Merge Strategy.

Author: DriftAdapt Contributors
Purpose: Implements the baseline arithmetic mean algorithm for LoRA adapters.
"""

from typing import Any, Dict, List, Optional

try:
    import torch
except ImportError:
    torch = None

from app.adapters.merge_exceptions import MergeFailed
from app.adapters.merge_strategy import AdapterMergeStrategy
from app.core.logging.logger_factory import LoggerFactory


class NaiveAverageMerge(AdapterMergeStrategy):
    """Computes the arithmetic mean of LoRA tensors across adapters."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("NaiveAverageMerge")
        
    def merge(self, states: List[Dict[str, Any]], weights: Optional[List[float]] = None) -> Dict[str, Any]:
        """Merges states by taking the arithmetic mean of each tensor.
        
        Args:
            states: List of state dictionaries to merge.
            weights: Ignored, as naive averaging implies uniform weights.
            
        Returns:
            The averaged state dictionary.
            
        Raises:
            MergeFailed: If PyTorch is unavailable or no states are provided.
        """
        if torch is None:
            raise MergeFailed("PyTorch is required for merge operations.")
            
        num_adapters = len(states)
        if num_adapters == 0:
            raise MergeFailed("No states provided for merging.")
            
        merged_state = {}
        base_keys = states[0].keys()
        
        for key in base_keys:
            # Stack all tensors for this key and compute the mean along dim 0
            tensors = [state[key] for state in states]
            stacked = torch.stack(tensors, dim=0)
            
            # Use torch.mean on float to prevent integer division truncation, then cast back
            mean_tensor = torch.mean(stacked.float(), dim=0).to(tensors[0].dtype)
            merged_state[key] = mean_tensor
            
        self._logger.debug(f"Computed arithmetic mean for {len(base_keys)} parameters across {num_adapters} adapters.")
        return merged_state
        
    def validate_inputs(self, states: List[Dict[str, Any]]) -> None:
        """Specific validation for naive averaging. 
        
        No mathematical constraints beyond structural matching exist for naive avg.
        """
        pass
        
    def supports_weighting(self) -> bool:
        """Naive averaging does not support custom client weighting (implies uniform)."""
        return False
        
    def strategy_name(self) -> str:
        """Returns the strategy identifier."""
        return "naive_average"

"""DriftAdapt Aggregation Validator.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, List
import torch

from app.aggregation.aggregation_exceptions import ValidationFailure


class AggregationValidator:
    """Validates adapters before and after merging."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        
    def validate_before_merge(self, adapter_state_dicts: List[Dict[str, torch.Tensor]]) -> bool:
        """Validates that all state dicts are compatible for merging."""
        if not adapter_state_dicts:
            raise ValidationFailure("No adapters provided for validation.")
            
        if len(adapter_state_dicts) == 1:
            return True
            
        base_keys = set(adapter_state_dicts[0].keys())
        for i, sd in enumerate(adapter_state_dicts[1:], start=1):
            keys = set(sd.keys())
            if base_keys != keys:
                raise ValidationFailure(f"Adapter at index {i} has mismatching keys.")
                
            for k in base_keys:
                if adapter_state_dicts[0][k].shape != sd[k].shape:
                    raise ValidationFailure(f"Tensor shape mismatch for key {k} at index {i}.")
                    
        return True
        
    def validate_after_merge(self, global_state_dict: Dict[str, torch.Tensor]) -> bool:
        """Validates the merged global adapter."""
        if not global_state_dict:
            raise ValidationFailure("Global adapter is empty.")
            
        for k, v in global_state_dict.items():
            if torch.is_floating_point(v) and torch.isnan(v).any():
                raise ValidationFailure(f"NaN detected in global adapter for key {k}.")
                
        return True

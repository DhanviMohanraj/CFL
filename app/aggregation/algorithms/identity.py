"""DriftAdapt Identity Aggregation Algorithm.

Author: DriftAdapt Contributors
"""

import torch
from typing import Dict, List, Any

from app.aggregation.algorithms.base_algorithm import BaseAlgorithm


class IdentityAggregation(BaseAlgorithm):
    """Returns the first adapter unchanged (for debugging)."""
    
    def aggregate(self, adapter_state_dicts: List[Dict[str, torch.Tensor]], metadata: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        if not adapter_state_dicts:
            return {}
            
        return adapter_state_dicts[0].copy()

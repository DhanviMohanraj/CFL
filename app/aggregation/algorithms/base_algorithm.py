"""DriftAdapt Base Algorithm.

Author: DriftAdapt Contributors
"""

import abc
import torch
from typing import Dict, List, Any


class BaseAlgorithm(abc.ABC):
    """Abstract base class for all aggregation algorithms."""
    
    @abc.abstractmethod
    def aggregate(self, adapter_state_dicts: List[Dict[str, torch.Tensor]], metadata: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        """Aggregates a list of adapter state dictionaries into a single global state dictionary."""
        pass

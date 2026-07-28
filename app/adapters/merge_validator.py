"""DriftAdapt Merge Validator.

Author: DriftAdapt Contributors
Purpose: Validates structural integrity of input state dictionaries.
"""

from typing import Any, Dict, List

try:
    import torch
except ImportError:
    torch = None

from app.adapters.merge_exceptions import (
    DuplicateAdapterError,
    EmptyMergeInput,
    IncompatibleAdapters,
    TensorShapeMismatch,
)
from app.core.logging.logger_factory import LoggerFactory


class MergeValidator:
    """Validates structural properties of state dictionaries for merging."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("MergeValidator")
        
    def validate_inputs(self, states: List[Dict[str, Any]], version_ids: List[str]) -> None:
        """Validates the input lists of states and version_ids.
        
        Args:
            states: List of state dictionaries to merge.
            version_ids: List of corresponding version IDs.
            
        Raises:
            EmptyMergeInput: If fewer than 2 adapters are provided.
            DuplicateAdapterError: If duplicate version IDs are found.
            IncompatibleAdapters: If parameter names or dtypes mismatch.
            TensorShapeMismatch: If tensor shapes do not match.
        """
        if not states or len(states) < 2:
            raise EmptyMergeInput("At least two adapters are required for merging.")
            
        if len(states) != len(version_ids):
            raise ValueError("Mismatched list lengths between states and version_ids.")
            
        if len(set(version_ids)) != len(version_ids):
            raise DuplicateAdapterError("Duplicate adapter IDs found in merge inputs.")
            
        if torch is None:
            return
            
        base_state = states[0]
        base_keys = set(base_state.keys())
        
        for i, state in enumerate(states[1:]):
            vid = version_ids[i+1]
            state_keys = set(state.keys())
            
            if base_keys != state_keys:
                raise IncompatibleAdapters(f"Parameter names mismatch between base and {vid}.")
                
            for k in base_keys:
                if base_state[k].shape != state[k].shape:
                    raise TensorShapeMismatch(f"Shape mismatch for {k} between base and {vid}.")
                    
                if base_state[k].dtype != state[k].dtype:
                    raise IncompatibleAdapters(f"Dtype mismatch for {k} between base and {vid}.")
                    
        self._logger.debug("Merge validation passed for tensor shapes and keys.")

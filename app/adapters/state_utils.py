"""DriftAdapt Adapter State Utils.

Author: DriftAdapt Contributors
Purpose: Extracts, manipulates, and compares LoRA adapter states from PEFT models.
"""

from typing import Any, Dict, Optional, Tuple

try:
    import torch
    from torch.nn import Module
except ImportError:
    torch = None
    Module = Any

from app.adapters.metrics import AdapterMetricsPublisher
from app.core.logging.logger_factory import LoggerFactory


class AdapterStateManager:
    """Manages the extraction and comparison of adapter states without modifying base models."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("AdapterStateManager")
        self._metrics = AdapterMetricsPublisher()
        
    def extract_state(self, peft_model: Module) -> Dict[str, Any]:
        """Extracts only LoRA parameters from a PEFT model.
        
        Never includes base model frozen parameters.
        
        Args:
            peft_model: The PEFT-wrapped PyTorch model.
            
        Returns:
            A dictionary containing only LoRA state tensors, cloned to CPU.
        """
        if torch is None:
            raise RuntimeError("PyTorch is required to extract states.")
            
        full_state = peft_model.state_dict()
        
        # We explicitly filter for 'lora_' to guarantee base params are ignored.
        adapter_state = {
            k: v.cpu().clone() for k, v in full_state.items() if "lora_" in k
        }
        
        param_count = self.count_parameters(adapter_state)
        self._metrics.publish("parameter_count", param_count)
        self._logger.debug(f"Extracted {len(adapter_state)} adapter tensors ({param_count} total parameters).")
        
        return adapter_state
        
    def load_state(self, peft_model: Module, state_dict: Dict[str, Any], strict: bool = False) -> Tuple[list, list]:
        """Loads an adapter state into a PEFT model.
        
        Args:
            peft_model: The PEFT-wrapped PyTorch model.
            state_dict: The LoRA state dictionary to load.
            strict: If True, enforces strict key matching. Usually False for adapters.
            
        Returns:
            Tuple of (missing_keys, unexpected_keys)
        """
        if torch is None:
            raise RuntimeError("PyTorch is required to load states.")
            
        missing, unexpected = peft_model.load_state_dict(state_dict, strict=strict)
        self._logger.debug(f"Loaded adapter state. Missing keys: {len(missing)}, Unexpected keys: {len(unexpected)}")
        return missing, unexpected
        
    def clone_state(self, state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Deep clones an adapter state."""
        if torch is None:
            return {k: v for k, v in state_dict.items()}
        return {k: v.clone() for k, v in state_dict.items()}
        
    def count_parameters(self, state_dict: Dict[str, Any]) -> int:
        """Counts the total scalar parameters in an adapter state."""
        if torch is None:
            return 0
        return sum(v.numel() for v in state_dict.values() if hasattr(v, "numel"))
        
    def compare_states(self, state_a: Dict[str, Any], state_b: Dict[str, Any]) -> bool:
        """Returns True if two adapter states are exactly equal."""
        if torch is None:
            return False
            
        if set(state_a.keys()) != set(state_b.keys()):
            return False
            
        for k, v_a in state_a.items():
            v_b = state_b[k]
            if v_a.shape != v_b.shape:
                return False
            if not torch.equal(v_a, v_b):
                return False
        return True


def calculate_size(state_dict: Dict[str, Any], serializer_instance: Optional[Any] = None) -> Dict[str, float]:
    """Calculates byte size, MB size, and abstract communication cost.
    
    Args:
        state_dict: The adapter state.
        serializer_instance: Optional serializer to use for estimation.
        
    Returns:
        Dictionary of size metrics.
    """
    if serializer_instance is not None:
        size_bytes = serializer_instance.estimate_size(state_dict)
    else:
        from app.adapters.serializer import AdapterSerializer
        size_bytes = AdapterSerializer().estimate_size(state_dict)
        
    size_kb = size_bytes / 1024.0
    size_mb = size_kb / 1024.0
    
    # Simple heuristic for abstract communication cost
    cost = size_mb * 0.1 
    
    return {
        "bytes": float(size_bytes),
        "kb": float(size_kb),
        "mb": float(size_mb),
        "communication_cost": float(cost)
    }

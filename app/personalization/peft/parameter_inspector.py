"""DriftAdapt PEFT Parameter Inspector.

Author: DriftAdapt Contributors
Purpose: Exposes utilities to inspect model parameter counts and requires_grad states.
"""

from typing import Dict, Any
from torch.nn import Module


class ParameterInspector:
    """Utility class to inspect trainable vs total parameters in PyTorch models."""

    @classmethod
    def inspect(cls, model: Module) -> Dict[str, Any]:
        """Calculates trainable parameters, total parameters, and the ratio.
        
        Args:
            model: The PyTorch module to inspect.
            
        Returns:
            Dictionary containing counts and ratio.
        """
        trainable_params = 0
        total_params = 0
        
        for _, param in model.named_parameters():
            num_params = param.numel()
            # If parameters are quantized (like bitsandbytes), numel() might not reflect true logical size, 
            # but for PEFT injected models, this standard traversal is accepted by HF.
            if num_params == 0 and hasattr(param, "ds_numel"):
                num_params = param.ds_numel
                
            total_params += num_params
            if param.requires_grad:
                trainable_params += num_params
                
        ratio = 0.0
        if total_params > 0:
            ratio = trainable_params / total_params
            
        return {
            "trainable_parameters": trainable_params,
            "total_parameters": total_params,
            "trainable_ratio": ratio
        }

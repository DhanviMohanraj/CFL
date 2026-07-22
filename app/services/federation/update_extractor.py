"""Update Extractor Service.

Author: DriftAdapt Contributors
Purpose: Extracts only trainable LoRA parameters from the model, ensuring frozen foundation weights are ignored.
"""

from typing import Dict, Any, Tuple
import torch
from torch.nn import Module
from sys import getsizeof

from app.core.logging import LoggerFactory


class UpdateExtractor:
    """Service to isolate and extract trainable parameters from a PEFT model."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("UpdateExtractor")

    def extract_parameters(self, model: Module) -> Tuple[Dict[str, Any], int, int]:
        """Extracts only the trainable LoRA parameters.
        
        Args:
            model: The PEFT-wrapped PyTorch model.
            
        Returns:
            Tuple containing:
            - state_dict: Dictionary mapping parameter names to their CPU-bound tensor values.
            - trainable_count: The total number of trainable parameters extracted.
            - update_size: Estimated byte size of the extracted state dictionary.
        """
        self._logger.info("Extracting trainable parameters for federated update...")
        
        state_dict: Dict[str, Any] = {}
        trainable_count = 0
        update_size = 0
        
        for name, param in model.named_parameters():
            if param.requires_grad:
                # Move to CPU and detach to prevent memory leaks during serialization
                param_cpu = param.detach().cpu().clone()
                state_dict[name] = param_cpu
                
                # Compute statistics
                numel = param.numel()
                trainable_count += numel
                
                # Estimate byte size (elements * bytes_per_element)
                element_size = param.element_size()
                update_size += numel * element_size
                
                # Add a bit of overhead for the dictionary keys
                update_size += getsizeof(name)
                
        self._logger.info(
            f"Extraction complete. Found {trainable_count:,} trainable parameters "
            f"across {len(state_dict)} layers. Estimated size: {update_size / (1024*1024):.2f} MB."
        )
        
        return state_dict, trainable_count, update_size

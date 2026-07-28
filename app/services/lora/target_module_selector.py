"""DriftAdapt Target Module Selector.

Author: DriftAdapt Contributors
Purpose: Automatically discovers Transformer attention and feed-forward projections if not explicitly provided.
"""

from typing import List, Set
from torch.nn import Module

from app.core.logging import LoggerFactory


class TargetModuleSelector:
    """Discovers target modules for LoRA injection dynamically based on model architecture."""

    # Common projection suffixes in Hugging Face models (Llama, Qwen, Mistral, etc.)
    COMMON_ATTN_PROJECTIONS = {"q_proj", "k_proj", "v_proj", "o_proj", "query_key_value"}
    COMMON_MLP_PROJECTIONS = {"gate_proj", "up_proj", "down_proj", "mlp.dense"}

    def __init__(self) -> None:
        """Initializes TargetModuleSelector."""
        self._logger = LoggerFactory.get_logger("TargetModuleSelector")

    def discover_modules(self, model: Module, include_mlp: bool = True) -> List[str]:
        """Inspects the model architecture and selects optimal target modules.
        
        Args:
            model: The base PyTorch foundation model.
            include_mlp: Whether to include MLP layers in addition to attention layers.
            
        Returns:
            A list of unique module name suffixes to inject LoRA into.
        """
        self._logger.info("Auto-discovering target modules for LoRA injection...")
        
        named_modules = [name for name, _ in model.named_modules()]
        selected_targets: Set[str] = set()

        search_space = self.COMMON_ATTN_PROJECTIONS.copy()
        if include_mlp:
            search_space.update(self.COMMON_MLP_PROJECTIONS)

        for module_name in named_modules:
            # We look for the last dot-separated part (e.g., 'model.layers.0.self_attn.q_proj' -> 'q_proj')
            suffix = module_name.split(".")[-1]
            if suffix in search_space:
                selected_targets.add(suffix)

        result = sorted(list(selected_targets))
        
        if not result:
            self._logger.warning("Auto-discovery found no standard transformer projections.")
            
        self._logger.info(f"Discovered {len(result)} target module types: {result}")
        return result

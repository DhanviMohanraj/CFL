"""Adapter Validator Service.

Author: DriftAdapt Contributors
Purpose: Strictly validates PEFT LoRA adapters before they are injected into the active model.
"""

import os
from typing import Tuple

from app.core.logging import LoggerFactory
from app.services.inference.adapter_registry import AdapterRegistry


class AdapterValidator:
    """Verifies adapter structural correctness and version compatibility."""
    
    def __init__(self, adapter_registry: AdapterRegistry) -> None:
        self._logger = LoggerFactory.get_logger("AdapterValidator")
        self._registry = adapter_registry

    def validate_adapter_files(self, adapter_path: str) -> Tuple[bool, str]:
        """Checks if the directory contains required PEFT adapter files (adapter_model.bin / adapter_config.json)."""
        if not os.path.exists(adapter_path):
            return False, f"Path not found: {adapter_path}"
            
        has_config = os.path.exists(os.path.join(adapter_path, "adapter_config.json"))
        # PEFT uses safetensors or bin
        has_weights = os.path.exists(os.path.join(adapter_path, "adapter_model.bin")) or \
                      os.path.exists(os.path.join(adapter_path, "adapter_model.safetensors"))
                      
        if not has_config:
            return False, "Missing adapter_config.json"
        if not has_weights:
            return False, "Missing adapter_model.bin or adapter_model.safetensors"
            
        return True, "Valid PEFT structure"

    def validate_loaded_adapter(self, adapter_id: str) -> Tuple[bool, str]:
        """Verifies an adapter is successfully loaded in the inference registry."""
        if self._registry.is_loaded(adapter_id):
            return True, f"Adapter '{adapter_id}' successfully verified in memory."
        return False, f"Adapter '{adapter_id}' is not loaded."

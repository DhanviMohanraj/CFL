"""Adapter Loader Service.

Author: DriftAdapt Contributors
Purpose: Manages loading PEFT adapters from the filesystem into the foundation model.
"""

import os
from typing import Optional

from app.core.logging import LoggerFactory
from app.services.inference.adapter_registry import AdapterRegistry
from app.models.foundation.model_manager import ModelManager


class AdapterLoader:
    """Handles I/O operations for LoRA adapter checkpoints during inference."""
    
    def __init__(self, model_manager: ModelManager, adapter_registry: AdapterRegistry) -> None:
        self._logger = LoggerFactory.get_logger("AdapterLoader")
        self._model_manager = model_manager
        self._registry = adapter_registry

    def load_adapter(self, adapter_id: str, adapter_path: str, version: str = "latest") -> bool:
        """Loads a PEFT adapter from disk into the foundation model.
        
        Args:
            adapter_id: The identifier for the adapter.
            adapter_path: Local filesystem path to the adapter checkpoint.
            version: The version string of the adapter.
            
        Returns:
            True if loaded successfully, False otherwise.
        """
        if self._registry.is_loaded(adapter_id):
            self._logger.info(f"Adapter {adapter_id} is already loaded.")
            return True
            
        if not os.path.exists(adapter_path):
            self._logger.error(f"Adapter path does not exist: {adapter_path}")
            return False
            
        try:
            self._logger.info(f"Loading adapter {adapter_id} from {adapter_path}")
            model = self._model_manager.get_model()
            if model is None:
                raise ValueError("Foundation model is not loaded.")
                
            # If PEFT model, use load_adapter
            if hasattr(model, "load_adapter"):
                model.load_adapter(adapter_path, adapter_name=adapter_id)
            else:
                self._logger.warning("Model does not natively support dynamic PEFT load_adapter in this context.")
                return False
                
            self._registry.register_adapter(
                adapter_id=adapter_id,
                adapter_name=os.path.basename(adapter_path),
                version=version
            )
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to load adapter {adapter_id}", error=str(e))
            return False

    def unload_adapter(self, adapter_id: str) -> bool:
        """Unloads an adapter from VRAM to free memory."""
        if not self._registry.is_loaded(adapter_id):
            return True
            
        try:
            model = self._model_manager.get_model()
            if model and hasattr(model, "delete_adapter"):
                model.delete_adapter(adapter_id)
                self._registry.unregister_adapter(adapter_id)
                self._logger.info(f"Successfully unloaded adapter {adapter_id}")
                return True
            return False
            
        except Exception as e:
            self._logger.error(f"Failed to unload adapter {adapter_id}", error=str(e))
            return False

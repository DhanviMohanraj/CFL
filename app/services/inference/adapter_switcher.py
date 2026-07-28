"""Adapter Switcher Service.

Author: DriftAdapt Contributors
Purpose: Rapidly multiplexes which LoRA adapter is actively responding to inference queries.
"""

from typing import Optional
import threading

from app.core.logging import LoggerFactory
from app.services.inference.adapter_registry import AdapterRegistry
from app.models.foundation.model_manager import ModelManager


class AdapterSwitcher:
    """Thread-safe service to switch the active PEFT adapter dynamically."""
    
    def __init__(self, model_manager: ModelManager, adapter_registry: AdapterRegistry) -> None:
        self._logger = LoggerFactory.get_logger("AdapterSwitcher")
        self._model_manager = model_manager
        self._registry = adapter_registry
        self._switch_lock = threading.Lock()

    def switch_adapter(self, target_adapter_id: Optional[str]) -> bool:
        """Switches the active inference adapter.
        
        Args:
            target_adapter_id: The ID to activate. None disables all adapters (base model only).
            
        Returns:
            True if successful.
        """
        with self._switch_lock:
            current_active = self._registry.get_active_adapter_id()
            if current_active == target_adapter_id:
                return True
                
            model = self._model_manager.get_model()
            if model is None:
                self._logger.error("Foundation model not loaded.")
                return False
                
            try:
                if target_adapter_id is None:
                    if hasattr(model, "disable_adapters"):
                        model.disable_adapters()
                        self._logger.info("Disabled all adapters. Running base model.")
                    else:
                        self._logger.warning("Model lacks disable_adapters support.")
                else:
                    if not self._registry.is_loaded(target_adapter_id):
                        self._logger.error(f"Cannot switch to unloaded adapter: {target_adapter_id}")
                        return False
                        
                    if hasattr(model, "set_adapter"):
                        if hasattr(model, "enable_adapters"):
                            model.enable_adapters()
                        model.set_adapter(target_adapter_id)
                        self._logger.info(f"Switched active adapter to {target_adapter_id}")
                    else:
                        self._logger.error("Model does not support set_adapter.")
                        return False
                        
                # Update registry state
                self._registry.set_active_adapter(target_adapter_id)
                return True
                
            except Exception as e:
                self._logger.error(f"Failed to switch adapter to {target_adapter_id}", error=str(e))
                # Attempt rollback to previous
                try:
                    if current_active:
                        model.set_adapter(current_active)
                    else:
                        if hasattr(model, "disable_adapters"):
                            model.disable_adapters()
                except Exception as rollback_err:
                    self._logger.critical(f"Rollback failed during adapter switch: {rollback_err}")
                return False

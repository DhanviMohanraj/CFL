"""Adapter Registry Service.

Author: DriftAdapt Contributors
Purpose: In-memory tracker for all loaded LoRA adapters in the inference engine.
"""

from typing import Dict, List, Optional
import time

from app.core.logging import LoggerFactory
from app.schemas.adapter_selection import AdapterSelection


class AdapterRegistry:
    """Manages metadata for LoRA adapters currently loaded in memory."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("AdapterRegistry")
        self._adapters: Dict[str, AdapterSelection] = {}
        self._active_adapter_id: Optional[str] = None

    def register_adapter(self, adapter_id: str, adapter_name: str, version: str = "latest", priority: int = 0) -> None:
        """Registers a newly loaded adapter."""
        selection = AdapterSelection(
            adapter_id=adapter_id,
            adapter_name=adapter_name,
            adapter_version=version,
            adapter_status="LOADED",
            load_timestamp=time.time(),
            priority=priority
        )
        self._adapters[adapter_id] = selection
        self._logger.info(f"Registered adapter: {adapter_id} (Version: {version})")

    def unregister_adapter(self, adapter_id: str) -> None:
        """Removes an adapter from the registry upon unloading."""
        if adapter_id in self._adapters:
            del self._adapters[adapter_id]
            self._logger.info(f"Unregistered adapter: {adapter_id}")
            if self._active_adapter_id == adapter_id:
                self._active_adapter_id = None

    def set_active_adapter(self, adapter_id: Optional[str]) -> bool:
        """Flags an adapter as currently active on the model (or None for base model)."""
        if adapter_id is None:
            if self._active_adapter_id and self._active_adapter_id in self._adapters:
                self._adapters[self._active_adapter_id].adapter_status = "LOADED"
            self._active_adapter_id = None
            self._logger.debug("Active adapter set to None (base model).")
            return True
            
        if adapter_id in self._adapters:
            # Demote old active
            if self._active_adapter_id and self._active_adapter_id in self._adapters:
                self._adapters[self._active_adapter_id].adapter_status = "LOADED"
                
            # Promote new active
            self._active_adapter_id = adapter_id
            self._adapters[adapter_id].adapter_status = "ACTIVE"
            self._logger.info(f"Active adapter switched to: {adapter_id}")
            return True
            
        self._logger.error(f"Cannot set active adapter to {adapter_id}: Not found in registry.")
        return False

    def get_active_adapter_id(self) -> Optional[str]:
        """Returns the ID of the currently active adapter."""
        return self._active_adapter_id

    def get_loaded_adapters(self) -> List[AdapterSelection]:
        """Returns a list of all loaded adapters."""
        return list(self._adapters.values())

    def is_loaded(self, adapter_id: str) -> bool:
        """Checks if an adapter is currently tracked in memory."""
        return adapter_id in self._adapters

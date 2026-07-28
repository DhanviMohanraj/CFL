"""DriftAdapt Adapter Registry Service.

Author: DriftAdapt Contributors
Purpose: Exposes an in-memory thread-safe registry to store, update, and fetch adapter metadata.
"""

import threading
from typing import Dict, List, Optional

from app.schemas.adapter_metadata import AdapterMetadataResponse
from app.core.logging import LoggerFactory


class AdapterRegistry:
    """In-memory thread-safe storage for initialized LoRA adapters."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("AdapterRegistry")
        self._registry: Dict[str, AdapterMetadataResponse] = {}
        self._lock = threading.Lock()

    def register(self, metadata: AdapterMetadataResponse) -> None:
        """Registers a new adapter.
        
        Args:
            metadata: The metadata response object to store.
            
        Raises:
            ValueError: If the adapter_id already exists.
        """
        with self._lock:
            if metadata.adapter_id in self._registry:
                raise ValueError(f"Adapter ID '{metadata.adapter_id}' already exists in registry.")
            self._registry[metadata.adapter_id] = metadata
            self._logger.info(f"Registered new adapter: {metadata.adapter_id} ({metadata.adapter_name})")

    def unregister(self, adapter_id: str) -> bool:
        """Removes an adapter from the registry.
        
        Args:
            adapter_id: The ID of the adapter to remove.
            
        Returns:
            True if removed, False if it did not exist.
        """
        with self._lock:
            if adapter_id in self._registry:
                del self._registry[adapter_id]
                self._logger.info(f"Unregistered adapter: {adapter_id}")
                return True
            return False

    def get_adapter(self, adapter_id: str) -> Optional[AdapterMetadataResponse]:
        """Fetches adapter metadata by ID."""
        with self._lock:
            return self._registry.get(adapter_id)

    def list_adapters(self) -> List[AdapterMetadataResponse]:
        """Lists all registered adapters."""
        with self._lock:
            return list(self._registry.values())

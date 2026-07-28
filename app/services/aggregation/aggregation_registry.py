"""Aggregation Registry Service.

Author: DriftAdapt Contributors
Purpose: Central runtime registry for active global adapters and registered edge clients.
"""

from typing import Dict, List, Optional

from app.core.logging import LoggerFactory
from app.schemas.global_adapter import GlobalAdapter


class AggregationRegistry:
    """Maintains active state of registered clients and the current global adapter."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("AggregationRegistry")
        self._global_adapters: Dict[str, GlobalAdapter] = {}
        self._registered_clients: set[str] = set()
        self._current_version_tag: Optional[str] = None

    def register_client(self, client_id: str) -> None:
        """Registers a client ID as actively participating in federation."""
        if client_id not in self._registered_clients:
            self._registered_clients.add(client_id)
            self._logger.debug(f"Registered new client: {client_id}")

    def get_registered_clients(self) -> List[str]:
        """Returns a list of all known registered clients."""
        return list(self._registered_clients)

    def register_global_adapter(self, adapter: GlobalAdapter) -> None:
        """Registers a newly merged global adapter and sets it as current."""
        self._global_adapters[adapter.adapter_version] = adapter
        self._current_version_tag = adapter.adapter_version
        self._logger.info(f"Registered new global adapter: {adapter.adapter_version}")

    def get_current_global_adapter(self) -> Optional[GlobalAdapter]:
        """Retrieves the most recent active global adapter."""
        if self._current_version_tag:
            return self._global_adapters.get(self._current_version_tag)
        return None

    def get_adapter_by_version(self, version_tag: str) -> Optional[GlobalAdapter]:
        """Retrieves a specific historical adapter."""
        return self._global_adapters.get(version_tag)

    def set_current_version(self, version_tag: str) -> bool:
        """Manually sets the current active version (useful for rollbacks)."""
        if version_tag in self._global_adapters:
            self._current_version_tag = version_tag
            self._logger.info(f"Current global adapter set to: {version_tag}")
            return True
        self._logger.error(f"Cannot set current version to {version_tag}: Not found in registry.")
        return False

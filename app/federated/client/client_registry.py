"""DriftAdapt Client Registry.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, Optional

from app.core.logging.logger_factory import LoggerFactory
from app.federated.client.client_exceptions import ClientRegistrationError
from app.federated.client.client_schema import ClientIdentity


class ClientRegistry:
    """Manages tracking of federated clients."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._logger = LoggerFactory.get_logger("ClientRegistry")
        self._clients: Dict[str, ClientIdentity] = {}
        
    def register(self, identity: ClientIdentity) -> None:
        with self._lock:
            if identity.client_id in self._clients:
                self._logger.warning(f"Overwriting existing client registration: {identity.client_id}")
            self._clients[identity.client_id] = identity
            self._logger.info(f"Registered client: {identity.client_id}")
            
    def unregister(self, client_id: str) -> None:
        with self._lock:
            if client_id in self._clients:
                del self._clients[client_id]
                self._logger.info(f"Unregistered client: {client_id}")
                
    def lookup(self, client_id: str) -> Optional[ClientIdentity]:
        with self._lock:
            return self._clients.get(client_id)
            
    def heartbeat(self, client_id: str) -> None:
        """Updates the status of an active client."""
        with self._lock:
            client = self._clients.get(client_id)
            if not client:
                raise ClientRegistrationError(f"Cannot heartbeat unknown client: {client_id}")
            client.status = "ACTIVE"
            
    def statistics(self) -> Dict[str, int]:
        with self._lock:
            active = sum(1 for c in self._clients.values() if c.status == "ACTIVE")
            return {
                "total_registered": len(self._clients),
                "active_clients": active,
                "offline_clients": len(self._clients) - active
            }

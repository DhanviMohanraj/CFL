"""DriftAdapt Synchronization Controller.

Author: DriftAdapt Contributors
"""

import threading
from typing import Set


class SynchronizationController:
    """Coordinates barriers between clients and the federated coordinator."""
    
    def __init__(self, expected_count: int) -> None:
        self.expected_count = expected_count
        self.completed_clients: Set[str] = set()
        self._lock = threading.RLock()
        self._event = threading.Event()
        
    def client_ready(self, client_id: str) -> None:
        """Marks a client as ready and releases barrier if all are ready."""
        with self._lock:
            self.completed_clients.add(client_id)
            if len(self.completed_clients) >= self.expected_count:
                self._event.set()
                
    def wait(self, timeout: float = None) -> bool:
        """Waits for all clients to be ready."""
        return self._event.wait(timeout)
        
    def reset(self) -> None:
        """Resets the barrier for the next phase."""
        with self._lock:
            self.completed_clients.clear()
            self._event.clear()
            
    def abort(self) -> None:
        """Aborts the barrier immediately."""
        self._event.set()

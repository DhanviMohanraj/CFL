"""DriftAdapt Synchronization Manager.

Author: DriftAdapt Contributors
Purpose: High-level orchestration of round synchronization.
"""

import threading
import time
from typing import Dict, List, Optional

from app.core.logging.logger_factory import LoggerFactory
from app.federated.communication.communication_exceptions import SynchronizationError
from app.federated.communication.communication_registry import CommunicationRegistry
from app.federated.communication.communication_schema import SynchronizationStatus


class SynchronizationManager:
    """Manages federated synchronization rounds."""
    
    def __init__(self, registry: CommunicationRegistry) -> None:
        self._registry = registry
        self._logger = LoggerFactory.get_logger("SynchronizationManager")
        self._lock = threading.RLock()
        self._active_syncs: Dict[str, SynchronizationStatus] = {}
        
    def begin_sync(self, session_id: str) -> SynchronizationStatus:
        """Starts tracking a synchronization session."""
        with self._lock:
            status = SynchronizationStatus(session_id=session_id)
            self._active_syncs[session_id] = status
            self._logger.info(f"Began synchronization {session_id}")
            return status
            
    def current_status(self, session_id: str) -> Optional[SynchronizationStatus]:
        """Returns current sync status."""
        with self._lock:
            return self._active_syncs.get(session_id)
            
    def complete_sync(self, session_id: str) -> None:
        """Marks a synchronization as successfully completed."""
        with self._lock:
            status = self._active_syncs.pop(session_id, None)
            if not status:
                raise SynchronizationError(f"No active sync for session {session_id}")
                
            status.current_state = "COMPLETED"
            status.last_updated = time.time()
            self._registry.add_sync_status(status)
            self._logger.info(f"Completed synchronization {session_id}")
            
    def rollback_sync(self, session_id: str) -> None:
        """Rolls back a failed synchronization."""
        with self._lock:
            status = self._active_syncs.pop(session_id, None)
            if not status:
                return
                
            status.current_state = "ROLLED_BACK"
            status.last_updated = time.time()
            self._registry.add_sync_status(status)
            self._logger.warning(f"Rolled back synchronization {session_id}")
            
    def history(self) -> List[SynchronizationStatus]:
        """Returns all past sync states."""
        return self._registry.get_sync_history()

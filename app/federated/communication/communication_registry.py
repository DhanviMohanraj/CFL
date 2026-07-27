"""DriftAdapt Communication Registry.

Author: DriftAdapt Contributors
Purpose: Thread-safe storage for active and historical communication sessions.
"""

import threading
from typing import Dict, List, Optional

from app.core.logging.logger_factory import LoggerFactory
from app.federated.communication.communication_schema import SynchronizationStatus
from app.federated.communication.communication_session import CommunicationSession


class CommunicationRegistry:
    """Tracks sessions and synchronization history."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._logger = LoggerFactory.get_logger("CommunicationRegistry")
        
        self._active_sessions: Dict[str, CommunicationSession] = {}
        self._completed_sessions: List[CommunicationSession] = []
        self._failed_sessions: List[CommunicationSession] = []
        self._sync_history: List[SynchronizationStatus] = []
        
    def register_session(self, session: CommunicationSession) -> None:
        """Registers a new active session."""
        with self._lock:
            self._active_sessions[session.session_id] = session
            self._logger.debug(f"Registered session {session.session_id}")
            
    def lookup_session(self, session_id: str) -> Optional[CommunicationSession]:
        """Looks up an active session."""
        with self._lock:
            return self._active_sessions.get(session_id)
            
    def remove_session(self, session_id: str) -> None:
        """Moves a session from active to completed or failed."""
        with self._lock:
            session = self._active_sessions.pop(session_id, None)
            if session:
                if session.state == "COMPLETED":
                    self._completed_sessions.append(session)
                else:
                    self._failed_sessions.append(session)
                    
    def add_sync_status(self, status: SynchronizationStatus) -> None:
        """Records a synchronization status."""
        with self._lock:
            self._sync_history.append(status)
            
    def get_sync_history(self) -> List[SynchronizationStatus]:
        """Returns the history of synchronization attempts."""
        with self._lock:
            return list(self._sync_history)
            
    def get_statistics(self) -> Dict[str, int]:
        """Returns global registry statistics."""
        with self._lock:
            return {
                "active_sessions": len(self._active_sessions),
                "completed_sessions": len(self._completed_sessions),
                "failed_sessions": len(self._failed_sessions),
                "total_syncs": len(self._sync_history)
            }

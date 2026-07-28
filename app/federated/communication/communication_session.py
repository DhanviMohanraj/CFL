"""DriftAdapt Communication Session.

Author: DriftAdapt Contributors
Purpose: Tracks a single communication session.
"""

import time
import uuid
from typing import List

from app.core.logging.logger_factory import LoggerFactory
from app.federated.communication.communication_exceptions import ProtocolError


class CommunicationSession:
    """Represents a session of communication."""
    
    VALID_STATES = ["CREATED", "PREPARING", "UPLOADING", "DOWNLOADING", "COMPLETED", "CANCELLED", "FAILED"]
    
    def __init__(self, sender: str, receiver: str) -> None:
        self.session_id = str(uuid.uuid4())
        self.sender = sender
        self.receiver = receiver
        self.state = "CREATED"
        self.created_at = time.time()
        self.updated_at = time.time()
        self.transferred_bytes = 0
        self.retries = 0
        self.history: List[str] = [f"{self.created_at}: Session created"]
        self._logger = LoggerFactory.get_logger("CommunicationSession")
        
    def _update_state(self, new_state: str) -> None:
        if new_state not in self.VALID_STATES:
            raise ProtocolError(f"Invalid state transition to {new_state}")
        self.state = new_state
        self.updated_at = time.time()
        self.history.append(f"{self.updated_at}: Transitioned to {new_state}")
        self._logger.debug(f"Session {self.session_id} state -> {new_state}")
        
    def set_preparing(self) -> None:
        self._update_state("PREPARING")
        
    def set_uploading(self) -> None:
        self._update_state("UPLOADING")
        
    def set_downloading(self) -> None:
        self._update_state("DOWNLOADING")
        
    def set_completed(self) -> None:
        self._update_state("COMPLETED")
        
    def set_cancelled(self) -> None:
        self._update_state("CANCELLED")
        
    def set_failed(self) -> None:
        self._update_state("FAILED")
        
    def add_bytes(self, amount: int) -> None:
        self.transferred_bytes += amount
        self.updated_at = time.time()
        
    def increment_retry(self) -> None:
        self.retries += 1
        self.updated_at = time.time()
        self.history.append(f"{self.updated_at}: Retry {self.retries}")

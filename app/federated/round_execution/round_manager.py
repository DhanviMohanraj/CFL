"""DriftAdapt Round Manager.

Author: DriftAdapt Contributors
"""

import uuid
import time
from typing import List, Dict, Any

from app.federated.round_execution.execution_schema import RoundMetadata
from app.federated.round_execution.round_registry import RoundRegistry


class RoundManager:
    """Manages the creation and termination of rounds."""
    
    def __init__(self, registry: RoundRegistry) -> None:
        self.registry = registry
        
    def start_round(self, month: int, epoch: int, clients: List[str]) -> str:
        """Initializes a new round and registers it."""
        round_id = str(uuid.uuid4())
        metadata = RoundMetadata(
            round_id=round_id,
            month=month,
            epoch=epoch,
            participating_clinics=clients,
            start_time=time.time(),
            status="STARTED"
        )
        self.registry.register(metadata)
        return round_id
        
    def finish_round(self, round_id: str, success: bool = True) -> None:
        """Marks a round as completed or failed."""
        metadata = self.registry.lookup(round_id)
        if metadata:
            metadata.status = "COMPLETED" if success else "FAILED"
            metadata.end_time = time.time()
            self.registry.archive(round_id)
            
    def cancel_round(self, round_id: str) -> None:
        """Cancels an active round."""
        metadata = self.registry.lookup(round_id)
        if metadata:
            metadata.status = "CANCELLED"
            metadata.end_time = time.time()
            self.registry.archive(round_id)

"""DriftAdapt Trainer Registry.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, List, Optional

from app.training.trainer_schema import TrainerMetadata


class TrainerRegistry:
    """Manages tracking of active and historical local trainers."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._active_trainers: Dict[str, TrainerMetadata] = {}
        self._archived_trainers: Dict[str, TrainerMetadata] = {}
        
    def register(self, metadata: TrainerMetadata) -> None:
        with self._lock:
            self._active_trainers[metadata.trainer_id] = metadata
            
    def lookup(self, trainer_id: str) -> Optional[TrainerMetadata]:
        with self._lock:
            if trainer_id in self._active_trainers:
                return self._active_trainers[trainer_id]
            return self._archived_trainers.get(trainer_id)
            
    def archive(self, trainer_id: str) -> None:
        with self._lock:
            metadata = self._active_trainers.pop(trainer_id, None)
            if metadata:
                self._archived_trainers[trainer_id] = metadata
                
    def statistics(self) -> Dict[str, int]:
        with self._lock:
            return {
                "active_count": len(self._active_trainers),
                "archived_count": len(self._archived_trainers)
            }
            
    def cleanup(self) -> None:
        with self._lock:
            self._active_trainers.clear()
            self._archived_trainers.clear()

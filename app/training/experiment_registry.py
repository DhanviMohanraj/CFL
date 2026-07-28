"""DriftAdapt Experiment Registry.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, List, Optional

from app.training.experiment_schema import ExperimentMetadata


class ExperimentRegistry:
    """Manages tracking of active and historical experiments."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._active_experiments: Dict[str, ExperimentMetadata] = {}
        self._archived_experiments: Dict[str, ExperimentMetadata] = {}
        
    def register(self, metadata: ExperimentMetadata) -> None:
        with self._lock:
            self._active_experiments[metadata.experiment_id] = metadata
            
    def lookup(self, experiment_id: str) -> Optional[ExperimentMetadata]:
        with self._lock:
            if experiment_id in self._active_experiments:
                return self._active_experiments[experiment_id]
            return self._archived_experiments.get(experiment_id)
            
    def archive(self, experiment_id: str) -> None:
        with self._lock:
            metadata = self._active_experiments.pop(experiment_id, None)
            if metadata:
                self._archived_experiments[experiment_id] = metadata
                
    def history(self) -> List[ExperimentMetadata]:
        with self._lock:
            return list(self._archived_experiments.values())
            
    def statistics(self) -> Dict[str, int]:
        with self._lock:
            return {
                "active_count": len(self._active_experiments),
                "archived_count": len(self._archived_experiments)
            }
            
    def cleanup(self) -> None:
        with self._lock:
            self._active_experiments.clear()
            self._archived_experiments.clear()

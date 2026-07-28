"""DriftAdapt Experiment History.

Author: DriftAdapt Contributors
"""

import json
import time
from typing import List, Dict, Any


class ExperimentHistory:
    """Maintains a complete audit log of the experiment."""
    
    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []
        
    def record_event(self, event_type: str, details: Dict[str, Any] = None) -> None:
        """Records an event in the history log."""
        self._events.append({
            "timestamp": time.time(),
            "type": event_type,
            "details": details or {}
        })
        
    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._events)
        
    def export_json(self) -> str:
        """Exports history to JSON format."""
        return json.dumps(self._events, indent=2)

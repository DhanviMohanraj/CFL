"""DriftAdapt Prototype Registry.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, Any


class PrototypeRegistry:
    """Maintains metadata about stored prototypes."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._registry: Dict[str, Dict[str, Any]] = {}
        
    def register(self, prototype_id: str, metadata: Dict[str, Any]) -> None:
        with self._lock:
            self._registry[prototype_id] = metadata
            
    def lookup(self, prototype_id: str) -> Dict[str, Any]:
        with self._lock:
            return self._registry.get(prototype_id, {})

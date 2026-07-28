"""DriftAdapt Prototype Bank.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, Any, List


class PrototypeBank:
    """Maintains a lightweight prototype memory."""
    
    def __init__(self, capacity: int = 512) -> None:
        self._capacity = capacity
        self._lock = threading.RLock()
        self._memory: Dict[str, Any] = {}
        
    def add(self, key: str, prototype: Any) -> None:
        with self._lock:
            if len(self._memory) >= self._capacity:
                # Evict oldest or least important
                oldest_key = next(iter(self._memory))
                del self._memory[oldest_key]
            self._memory[key] = prototype
            
    def get(self, key: str) -> Any:
        with self._lock:
            return self._memory.get(key)
            
    def clear(self) -> None:
        with self._lock:
            self._memory.clear()

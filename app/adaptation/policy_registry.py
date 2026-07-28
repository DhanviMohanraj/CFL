"""DriftAdapt Policy Registry.

Author: DriftAdapt Contributors
"""

import threading
from typing import Dict, Any, Optional


class PolicyRegistry:
    """Registers and provides access to adaptation policies."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._policies: Dict[str, Any] = {}
        
    def register(self, name: str, policy: Any) -> None:
        with self._lock:
            self._policies[name.lower()] = policy
            
    def lookup(self, name: str) -> Optional[Any]:
        with self._lock:
            return self._policies.get(name.lower())
            
    def all_policies(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._policies)

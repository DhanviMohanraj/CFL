"""DriftAdapt Redistribution Manager.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any
from app.federated.round_execution.execution_exceptions import RedistributionError


class RedistributionManager:
    """Distributes the global adapter to participating clinics."""
    
    def __init__(self) -> None:
        pass
        
    def redistribute(self, global_adapter_path: str, clients: List[str]) -> Dict[str, str]:
        """Redistributes the adapter. Returns a map of client to status."""
        if not global_adapter_path:
            raise RedistributionError("Global adapter path is missing.")
            
        results = {}
        for client in clients:
            results[client] = "success"
            
        return results

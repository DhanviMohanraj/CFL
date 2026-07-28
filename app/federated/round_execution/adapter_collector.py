"""DriftAdapt Adapter Collector.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any, Tuple
from app.federated.round_execution.execution_exceptions import AdapterCollectionError


class AdapterCollector:
    """Collects updated adapters from participating clients."""
    
    def __init__(self) -> None:
        pass
        
    def collect_adapters(self, clients: List[str]) -> List[Tuple[str, Dict[str, Any]]]:
        """Mocks collection of adapters."""
        collected = []
        for client in clients:
            path = f"exports/{client}_adapter.pt"
            metadata = {"checksum": "mock_checksum", "clinic_id": client}
            collected.append((path, metadata))
        
        if not collected:
            raise AdapterCollectionError("Failed to collect any adapters.")
            
        return collected

"""DriftAdapt Aggregation Context.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, List


class AggregationContext:
    """Holds contextual information for an aggregation run."""
    
    def __init__(self, round_id: str, config: Dict[str, Any], clients: List[str]) -> None:
        self.round_id = round_id
        self.config = config
        self.clients = clients
        self.adapter_paths: List[str] = []
        self.adapter_metadata: List[Dict[str, Any]] = []
        
    def add_adapter(self, client_id: str, path: str, metadata: Dict[str, Any]) -> None:
        """Adds an adapter to the context."""
        self.adapter_paths.append(path)
        self.adapter_metadata.append({"client_id": client_id, **metadata})

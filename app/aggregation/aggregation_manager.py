"""DriftAdapt Aggregation Manager.

Author: DriftAdapt Contributors
"""

import uuid
import time
from typing import List, Dict, Any

from app.aggregation.aggregation_schema import AggregationMetadata
from app.aggregation.aggregation_registry import AggregationRegistry


class AggregationManager:
    """Manages the creation and tracking of aggregation runs."""
    
    def __init__(self, registry: AggregationRegistry) -> None:
        self.registry = registry
        
    def start_aggregation(self, round_id: str, algorithm: str, clients: List[str]) -> AggregationMetadata:
        """Initializes a new aggregation event and registers it."""
        metadata = AggregationMetadata(
            round_id=round_id,
            algorithm=algorithm,
            participating_clinics=clients,
            start_time=time.time(),
            status="STARTED"
        )
        self.registry.register(metadata)
        return metadata
        
    def finish_aggregation(self, round_id: str, success: bool = True, version: str = None, checksum: str = None, metrics: Dict[str, Any] = None) -> None:
        """Marks an aggregation as completed or failed."""
        metadata = self.registry.lookup(round_id)
        if metadata:
            metadata.status = "COMPLETED" if success else "FAILED"
            metadata.end_time = time.time()
            metadata.duration = metadata.end_time - metadata.start_time
            if version:
                metadata.global_adapter_version = version
            if checksum:
                metadata.checksum = checksum
            if metrics:
                metadata.metrics = metrics

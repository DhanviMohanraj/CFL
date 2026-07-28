"""DriftAdapt Knowledge Consolidation Manager.

Author: DriftAdapt Contributors
"""

from app.knowledge.consolidation_registry import ConsolidationRegistry
from app.knowledge.consolidation_schema import ConsolidationRecord


class ConsolidationManager:
    """Manages knowledge consolidation records."""
    
    def __init__(self, registry: ConsolidationRegistry) -> None:
        self.registry = registry
        
    def track_consolidation(self, record: ConsolidationRecord) -> None:
        """Registers a completed consolidation."""
        self.registry.register(record)

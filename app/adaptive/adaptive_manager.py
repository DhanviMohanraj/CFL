"""DriftAdapt Adaptive Manager.

Author: DriftAdapt Contributors
"""

from app.adaptive.adaptive_registry import AdaptiveRegistry
from app.adaptive.adaptive_schema import AdaptiveRecord


class AdaptiveManager:
    """Manages adaptive execution records."""
    
    def __init__(self, registry: AdaptiveRegistry) -> None:
        self.registry = registry
        
    def track_execution(self, record: AdaptiveRecord) -> None:
        """Registers a completed execution."""
        self.registry.register(record)

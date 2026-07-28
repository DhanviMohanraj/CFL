"""DriftAdapt Drift Manager.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, List
from app.drift.drift_registry import DriftRegistry
from app.drift.drift_schema import DriftReport


class DriftManager:
    """Manages the state and tracking of drift analysis."""
    
    def __init__(self, registry: DriftRegistry) -> None:
        self.registry = registry
        
    def track_report(self, report: DriftReport) -> None:
        """Registers a completed drift report."""
        self.registry.register(report)

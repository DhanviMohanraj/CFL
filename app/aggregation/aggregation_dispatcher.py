"""DriftAdapt Aggregation Dispatcher.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, List


class AggregationDispatcher:
    """Dispatches the aggregation request to the engine."""
    
    def __init__(self, engine: Any) -> None:
        self.engine = engine
        
    def dispatch(self, round_id: str, adapter_paths: List[str]) -> str:
        """Invokes the aggregation engine."""
        return self.engine.aggregate(round_id, adapter_paths)

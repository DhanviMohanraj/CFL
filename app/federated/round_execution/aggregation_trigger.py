"""DriftAdapt Aggregation Trigger.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any
from app.federated.round_execution.execution_exceptions import AggregationTriggerError


class AggregationTrigger:
    """Triggers the aggregation dispatcher."""
    
    def __init__(self) -> None:
        pass
        
    def trigger_aggregation(self, round_id: str, adapters: List[str]) -> str:
        """Invokes the aggregation module with validated adapters."""
        if not adapters:
            raise AggregationTriggerError("No adapters provided for aggregation.")
            
        # Mocking the call to Module 5.4 or aggregation dispatcher
        global_adapter_path = f"exports/{round_id}_global_adapter.pt"
        return global_adapter_path

"""DriftAdapt Aggregation Dispatcher.

Author: DriftAdapt Contributors
"""

from app.training.experiment_exceptions import AggregationDispatchError


class AggregationDispatcher:
    """Dispatches the aggregation trigger to the coordinator/merge engine."""
    
    def __init__(self) -> None:
        pass
        
    def dispatch_aggregation(self, round_id: str) -> None:
        """Triggers aggregation for a round."""
        if not round_id:
            raise AggregationDispatchError("round_id is required to trigger aggregation.")
        # Mocks actual aggregation dispatch logic
        pass

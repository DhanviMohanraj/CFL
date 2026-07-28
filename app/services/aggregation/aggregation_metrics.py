"""Aggregation Metrics Service.

Author: DriftAdapt Contributors
Purpose: Computes analytical metrics such as bandwidth cost, average weights, and efficiency ratios.
"""

from typing import List, Dict, Any

from app.core.logging import LoggerFactory
from app.schemas.client_update_record import ClientUpdateRecord
from app.schemas.aggregation_statistics import AggregationStatistics


class AggregationMetrics:
    """Computes round statistics for federated aggregation."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("AggregationMetrics")

    def compute_statistics(
        self,
        accepted_updates: List[ClientUpdateRecord],
        rejected_updates: List[ClientUpdateRecord],
        aggregation_duration_s: float,
        parameter_count: int = 0
    ) -> AggregationStatistics:
        """Calculates comprehensive metrics for the round.
        
        Args:
            accepted_updates: Updates successfully merged.
            rejected_updates: Updates discarded by validators/filters.
            aggregation_duration_s: Mathematical merging duration.
            parameter_count: Number of parameters in the merged adapter.
            
        Returns:
            AggregationStatistics schema object.
        """
        total_updates = len(accepted_updates) + len(rejected_updates)
        efficiency = (len(accepted_updates) / total_updates) if total_updates > 0 else 0.0
        
        avg_weight = 0.0
        if accepted_updates:
            avg_weight = sum(u.update_weight for u in accepted_updates) / len(accepted_updates)
            
        # Mock communication cost (bandwidth). In a true implementation, we'd sum the payload bytes.
        # Assuming typical LoRA adapter size (e.g., ~15MB for a rank 8 3B model)
        comm_cost_mb = float(len(accepted_updates) * 15.0)
        
        stats = AggregationStatistics(
            average_client_weight=avg_weight,
            discarded_updates=len(rejected_updates),
            aggregation_time=aggregation_duration_s,
            communication_cost=comm_cost_mb,
            parameter_count=parameter_count,
            memory_usage=0.0, # Placeholder, can be integrated with resource_monitor later
            aggregation_efficiency=efficiency
        )
        
        self._logger.debug(f"Computed aggregation stats: Efficiency={efficiency:.2f}, Cost={comm_cost_mb}MB")
        
        return stats

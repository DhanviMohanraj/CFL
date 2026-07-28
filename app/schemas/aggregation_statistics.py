"""Aggregation Statistics Schema.

Author: DriftAdapt Contributors
Purpose: Captures metrics and statistics from a federated aggregation round.
"""

from pydantic import BaseModel, Field


class AggregationStatistics(BaseModel):
    """Metrics produced during the federated aggregation process."""
    
    average_client_weight: float = Field(default=0.0, description="Average weight applied across clients")
    discarded_updates: int = Field(default=0, description="Number of client updates rejected by validators")
    aggregation_time: float = Field(default=0.0, description="Total duration of the aggregation execution in seconds")
    communication_cost: float = Field(default=0.0, description="Estimated bandwidth cost of the round in MB")
    parameter_count: int = Field(default=0, description="Total number of parameters aggregated")
    memory_usage: float = Field(default=0.0, description="Peak memory usage during merge operation in MB")
    aggregation_efficiency: float = Field(default=0.0, description="Ratio of successful merges to total received updates")

"""Aggregation Request Schema.

Author: DriftAdapt Contributors
Purpose: Defines the parameters and criteria for a federated aggregation round.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AggregationRequest(BaseModel):
    """Configuration for triggering an aggregation round."""
    
    communication_round: int = Field(..., description="The current global communication round")
    aggregation_algorithm: str = Field(default="fedavg", description="Algorithm to use (e.g., 'fedavg', 'weighted_fedavg')")
    participating_clients: List[str] = Field(default_factory=list, description="Explicit list of client IDs to include. Empty means all available.")
    weighting_strategy: str = Field(default="equal", description="Strategy for weighting (e.g., 'equal', 'dataset_size')")
    minimum_clients: int = Field(default=2, description="Minimum number of valid client updates required to aggregate")
    timeout: float = Field(default=300.0, description="Timeout in seconds for waiting on client updates")
    aggregation_timestamp: float = Field(..., description="Unix timestamp when aggregation was requested")

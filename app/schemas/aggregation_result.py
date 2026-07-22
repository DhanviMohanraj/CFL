"""Aggregation Result Schema.

Author: DriftAdapt Contributors
Purpose: Defines the output payload returned after an aggregation cycle completes.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.aggregation_statistics import AggregationStatistics


class AggregationResult(BaseModel):
    """The final outcome and metadata of an aggregation process."""
    
    success: bool = Field(..., description="Whether the aggregation successfully produced a new adapter")
    communication_round: int = Field(..., description="The communication round that was executed")
    aggregated_clients: List[str] = Field(default_factory=list, description="List of client IDs whose updates were successfully merged")
    discarded_clients: List[str] = Field(default_factory=list, description="List of client IDs whose updates were rejected or failed")
    aggregation_duration: float = Field(default=0.0, description="Time taken to aggregate in seconds")
    algorithm_used: str = Field(..., description="The aggregation algorithm applied")
    global_adapter_version: Optional[str] = Field(default=None, description="The newly created version tag for the global adapter")
    aggregation_statistics: AggregationStatistics = Field(default_factory=AggregationStatistics, description="Detailed metrics of the round")
    error_message: Optional[str] = Field(default=None, description="Error reason if aggregation failed")

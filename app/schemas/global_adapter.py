"""Global Adapter Schema.

Author: DriftAdapt Contributors
Purpose: Defines the structure and metadata of the merged, canonical global LoRA adapter.
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

from app.schemas.aggregation_metadata import AggregationMetadata


class GlobalAdapter(BaseModel):
    """The final product of a federated aggregation round."""
    
    adapter_version: str = Field(..., description="Unique version tag (e.g., 'v1.0.0-round5')")
    communication_round: int = Field(..., description="The federated round number this adapter represents")
    parameter_count: int = Field(default=0, description="Total trainable parameters in this adapter")
    participating_clients: List[str] = Field(default_factory=list, description="IDs of the clients whose updates formed this global adapter")
    creation_timestamp: float = Field(..., description="Unix timestamp of when the merge completed")
    checksum: str = Field(..., description="SHA-256 hash of the global adapter weights")
    storage_location: Optional[str] = Field(default=None, description="Path or URI where the global weights are saved")
    metadata: AggregationMetadata = Field(..., description="Environmental context of the aggregation")
    
    # Exclude state dict from standard serialization due to PyTorch tensors
    state_dict: Optional[Dict[str, Any]] = Field(default=None, exclude=True, description="The actual merged PyTorch weights in memory")

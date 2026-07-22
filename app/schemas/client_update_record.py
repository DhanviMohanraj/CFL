"""Client Update Record Schema.

Author: DriftAdapt Contributors
Purpose: Represents the metadata and payload state of a received client update on the server.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ClientUpdateRecord(BaseModel):
    """Internal server representation of an incoming client update."""
    
    client_id: str = Field(..., description="Unique identifier of the client device")
    adapter_id: str = Field(..., description="Local adapter ID assigned by the client")
    local_epoch: int = Field(default=1, description="Number of local epochs trained by the client")
    personalization_round: int = Field(default=1, description="Local continual learning round")
    dataset_size: int = Field(default=0, description="Size of the local dataset used for training")
    update_weight: float = Field(default=1.0, description="Pre-calculated aggregation weight for this client")
    checksum: str = Field(..., description="SHA-256 checksum of the extracted LoRA payload")
    validation_status: str = Field(default="PENDING", description="Validation state: PENDING, VALID, INVALID, CORRUPTED")
    upload_timestamp: float = Field(..., description="Unix timestamp when the server received the update")
    # For a true distributed system, we would store an S3 URI or filepath, but here we store the raw bytes directly
    # or assume it's loaded in memory dynamically. We keep this schema for metadata tracking.
    payload_storage_path: Optional[str] = Field(default=None, description="Local or remote path to the binary payload")

"""DriftAdapt Client Schema.

Author: DriftAdapt Contributors
"""

import time
from typing import Dict, Any, List

from pydantic import BaseModel, Field


class TrainingEpochResult(BaseModel):
    """Metrics for a single training epoch."""
    epoch: int = Field(..., description="Epoch number.")
    loss: float = Field(..., description="Training loss for the epoch.")
    validation_score: float = Field(default=0.0, description="Validation score for the epoch.")
    timestamp: float = Field(default_factory=time.time)


class ClientIdentity(BaseModel):
    """Identity configuration for the federated client."""
    client_id: str = Field(..., description="Unique clinic/client identifier.")
    hardware_profile: str = Field(default="unknown", description="Hardware capability tag.")
    registered_at: float = Field(default_factory=time.time)
    status: str = Field(default="ACTIVE")


class CheckpointMetadata(BaseModel):
    """Metadata regarding a saved checkpoint."""
    checkpoint_id: str = Field(..., description="Unique ID for the checkpoint.")
    epoch: int = Field(..., description="Epoch at which this was saved.")
    path: str = Field(..., description="File path to the checkpoint.")
    timestamp: float = Field(default_factory=time.time)
    loss: float = Field(..., description="Loss at the time of checkpoint.")

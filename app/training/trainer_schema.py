"""DriftAdapt Trainer Schema.

Author: DriftAdapt Contributors
"""

import time
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field


class TrainerMetadata(BaseModel):
    """Metadata regarding a local training session."""
    trainer_id: str = Field(..., description="Unique ID for the trainer instance.")
    clinic_id: str = Field(..., description="The ID of the clinic executing the training.")
    month: int = Field(..., description="The simulated month being trained on.")
    start_time: float = Field(default_factory=time.time)
    end_time: Optional[float] = None
    status: str = Field(default="CREATED", description="Current status of the trainer.")
    config: Dict[str, Any] = Field(default_factory=dict, description="Training configuration details.")
    current_epoch: int = Field(default=0, description="The current training epoch.")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Recorded evaluation metrics.")

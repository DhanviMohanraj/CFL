"""DriftAdapt Personalization Request Schema.

Author: DriftAdapt Contributors
Purpose: Pydantic schema for initiating a local fine-tuning run.
"""

from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.training_config import TrainingConfiguration


class PersonalizationRequest(BaseModel):
    """API payload to start local personalization."""

    client_id: str = Field(..., description="Unique ID for the edge client.")
    adapter_id: str = Field(..., description="ID of the adapter to train.")
    dataset_path: str = Field(..., description="Path to the local dataset.")
    configuration: TrainingConfiguration = Field(..., description="Training hyperparameters.")
    resume_checkpoint: Optional[str] = Field(None, description="Path to checkpoint if resuming.")
    continual_learning_round: int = Field(1, ge=1, description="Current CL round.")
    personalization_mode: str = Field("supervised", description="Mode of training (e.g. supervised, dpo).")

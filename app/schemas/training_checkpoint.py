"""DriftAdapt Training Checkpoint Schema.

Author: DriftAdapt Contributors
Purpose: Pydantic schema representing saved checkpoint metadata.
"""

from pydantic import BaseModel, Field


class TrainingCheckpoint(BaseModel):
    """Metadata representing a saved state of training."""

    checkpoint_id: str = Field(..., description="Unique identifier for the checkpoint.")
    adapter_id: str = Field(..., description="The ID of the adapter being trained.")
    epoch: float = Field(..., description="The epoch this checkpoint was saved at.")
    optimizer_state_saved: bool = Field(..., description="Whether optimizer states are included.")
    scheduler_state_saved: bool = Field(..., description="Whether scheduler states are included.")
    model_state_saved: bool = Field(..., description="Whether adapter weights are included.")
    timestamp: str = Field(..., description="ISO-8601 timestamp of creation.")
    training_round: int = Field(1, description="Continual learning round number.")
    file_path: str = Field(..., description="Local path to the checkpoint directory.")

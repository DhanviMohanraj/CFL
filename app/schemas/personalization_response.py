"""DriftAdapt Personalization Response Schema.

Author: DriftAdapt Contributors
Purpose: Pydantic schema for returning the outcome of a fine-tuning run.
"""

from typing import Optional
from pydantic import BaseModel, Field


class PersonalizationResponse(BaseModel):
    """API response summarizing the training result."""

    success: bool = Field(..., description="Whether training completed successfully.")
    training_time_s: float = Field(..., description="Total training duration in seconds.")
    epochs_completed: float = Field(..., description="Total epochs run.")
    final_loss: float = Field(..., description="Loss at the end of training.")
    best_loss: Optional[float] = Field(None, description="Best validation loss encountered.")
    checkpoint_location: Optional[str] = Field(None, description="Path to the best/final checkpoint.")
    adapter_id: str = Field(..., description="The ID of the updated adapter.")
    updated_parameters: int = Field(..., description="Number of parameters updated.")
    status: str = Field(..., description="Status message (e.g., COMPLETED, INTERRUPTED).")

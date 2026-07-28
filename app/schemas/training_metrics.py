"""DriftAdapt Training Metrics Schema.

Author: DriftAdapt Contributors
Purpose: Pydantic schema for logging training and validation metrics per epoch/step.
"""

from typing import Optional
from pydantic import BaseModel, Field


class TrainingMetrics(BaseModel):
    """Snapshot of metrics during training."""

    epoch: float = Field(..., description="Current epoch (can be fractional for steps).")
    training_loss: float = Field(..., description="Average training loss.")
    validation_loss: Optional[float] = Field(None, description="Validation loss if evaluated.")
    accuracy: Optional[float] = Field(None, description="Task specific accuracy.")
    learning_rate: float = Field(..., description="Current learning rate.")
    gradient_norm: float = Field(..., description="L2 norm of the gradients.")
    gpu_memory_mb: float = Field(..., description="Allocated GPU memory in MB.")
    cpu_memory_mb: float = Field(..., description="Allocated CPU memory in MB.")
    throughput: float = Field(..., description="Samples processed per second.")
    elapsed_time_s: float = Field(..., description="Elapsed training time in seconds.")

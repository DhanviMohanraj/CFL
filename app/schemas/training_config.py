"""DriftAdapt Training Configuration Schema.

Author: DriftAdapt Contributors
Purpose: Pydantic schema for validating hyperparameters for the local training engine.
"""

from pydantic import BaseModel, Field


class TrainingConfiguration(BaseModel):
    """Configuration for local LoRA fine-tuning."""

    learning_rate: float = Field(2e-4, gt=0.0, description="Optimizer learning rate.")
    batch_size: int = Field(8, gt=0, description="Per-device batch size.")
    epochs: int = Field(3, gt=0, description="Number of training epochs.")
    optimizer: str = Field("adamw", pattern="^(adamw|sgd|adafactor)$", description="Optimizer type.")
    scheduler: str = Field("cosine", pattern="^(linear|cosine|polynomial|constant)$", description="Learning rate scheduler.")
    gradient_accumulation_steps: int = Field(1, gt=0, description="Steps before performing an optimization step.")
    warmup_steps: int = Field(100, ge=0, description="Number of steps for LR warmup.")
    max_grad_norm: float = Field(1.0, gt=0.0, description="Maximum gradient norm for clipping.")
    weight_decay: float = Field(0.01, ge=0.0, description="L2 weight decay penalty.")
    checkpoint_interval: int = Field(100, gt=0, description="Steps between saving checkpoints.")
    evaluation_interval: int = Field(100, gt=0, description="Steps between validation runs.")
    seed: int = Field(42, description="Random seed for reproducibility.")
    mixed_precision: bool = Field(True, description="Enable torch.amp mixed precision.")
    gradient_checkpointing: bool = Field(False, description="Enable gradient checkpointing for memory savings.")

"""DriftAdapt LoRA Configuration Schema.

Author: DriftAdapt Contributors
Purpose: Pydantic schema for validating incoming API requests for adapter initialization.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class LoRAConfigurationRequest(BaseModel):
    """API payload for initializing a new LoRA adapter."""

    adapter_name: str = Field(..., description="Unique identifier for the adapter.")
    r: int = Field(8, ge=1, description="Rank of the LoRA update matrices.")
    lora_alpha: float = Field(16.0, gt=0.0, description="LoRA scaling factor.")
    lora_dropout: float = Field(0.05, ge=0.0, le=1.0, description="Dropout probability.")
    bias: str = Field("none", pattern="^(none|all|lora_only)$", description="Bias training strategy.")
    task_type: str = Field("CAUSAL_LM", description="Task type (e.g., CAUSAL_LM, SEQ_2_SEQ_LM).")
    target_modules: Optional[List[str]] = Field(None, description="Modules to inject LoRA into. If None, auto-discovered.")
    inference_mode: bool = Field(False, description="Whether the adapter is for inference only.")
    initialization_method: str = Field("default", description="Initialization method (default, loftq, etc).")

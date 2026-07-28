"""Validation Result Schema.

Author: DriftAdapt Contributors
Purpose: Defines the output of a completed validation pass.
"""

import time
from typing import List, Optional
from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """The final status payload resulting from a validation run."""
    
    success: bool = Field(..., description="True if all checked subsystems passed validation")
    validation_id: str = Field(..., description="ID of the originating ValidationRequest")
    validation_status: str = Field(default="COMPLETED", description="Overall execution status")
    
    adapter_status: str = Field(default="NOT_CHECKED", description="Status of PEFT adapter validation (e.g. PASSED, FAILED)")
    model_status: str = Field(default="NOT_CHECKED", description="Status of base model integrity checks")
    inference_status: str = Field(default="NOT_CHECKED", description="Status of prompt/generation pipeline")
    integrity_status: str = Field(default="NOT_CHECKED", description="Status of checksum and weight corruption checks")
    
    execution_time: float = Field(default=0.0, description="Total time taken to run validation suite (seconds)")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal anomalies detected")
    errors: List[str] = Field(default_factory=list, description="Fatal errors causing validation failure")
    
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp of completion")

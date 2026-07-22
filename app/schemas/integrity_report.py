"""Integrity Report Schema.

Author: DriftAdapt Contributors
Purpose: Captures parameter-level verification metadata for models and adapters.
"""

import time
from typing import Optional
from pydantic import BaseModel, Field


class IntegrityReport(BaseModel):
    """Result of scanning the neural network weights for corruption or unsanctioned modification."""
    
    model_checksum: str = Field(default="unknown", description="Hash of the base model weights")
    adapter_checksum: Optional[str] = Field(default=None, description="Hash of the PEFT adapter weights, if applicable")
    
    parameter_count: int = Field(default=0, description="Total parameters in the base model")
    trainable_parameter_count: int = Field(default=0, description="Number of parameters requiring gradients (should only be adapter)")
    frozen_parameter_count: int = Field(default=0, description="Number of frozen base parameters")
    
    integrity_score: float = Field(default=100.0, description="Heuristic score representing structural confidence (0-100)")
    corruption_detected: bool = Field(default=False, description="True if any frozen weights have shifted unexpectedly")
    
    validation_timestamp: float = Field(default_factory=time.time, description="Unix timestamp of the integrity scan")

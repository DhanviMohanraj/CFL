"""Validation Request Schema.

Author: DriftAdapt Contributors
Purpose: Defines the parameters for running a system validation pass.
"""

import time
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field


class ValidationRequest(BaseModel):
    """Payload for triggering a system validation sweep."""
    
    validation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this validation run")
    validation_type: str = Field(default="full", description="Type of validation (e.g., 'full', 'quick', 'integrity_only')")
    adapter_id: Optional[str] = Field(default=None, description="Specific adapter to validate, if any")
    model_version: Optional[str] = Field(default="latest", description="Target model version")
    benchmark_enabled: bool = Field(default=True, description="Whether to also execute performance benchmarks")
    validation_scope: List[str] = Field(
        default_factory=lambda: ["model", "adapter", "inference"], 
        description="Subsystems to include in the validation run"
    )
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp of request")

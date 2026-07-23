"""DriftAdapt Adapter State Schemas.

Author: DriftAdapt Contributors
Purpose: Strictly models structured metadata and validation reports for adapter state utilities.
"""

import time
from typing import List

from pydantic import BaseModel, Field


class AdapterStateMetadata(BaseModel):
    """Metadata representing an exported or serialized LoRA adapter."""

    adapter_id: str = Field(..., description="Globally unique identifier for the adapter.")
    clinic_id: str = Field(..., description="The clinic ID that owns this adapter.")
    round_number: int = Field(..., description="The federated communication round.")
    parameter_count: int = Field(..., description="Number of parameters in the adapter state.")
    byte_size: int = Field(..., description="Size of the serialized adapter in bytes.")
    checksum: str = Field(..., description="SHA256 checksum of the serialized adapter.")
    serialization_format: str = Field(..., description="Format of serialization, e.g., 'torch'.")
    created_at: float = Field(
        default_factory=time.time,
        description="POSIX epoch timestamp of when the metadata was generated."
    )


class ValidationReport(BaseModel):
    """Structured report detailing the outcome of state validation."""

    success: bool = Field(..., description="True if validation passed with no critical errors.")
    errors: List[str] = Field(default_factory=list, description="List of critical validation errors.")
    warnings: List[str] = Field(default_factory=list, description="List of non-critical validation warnings.")
    parameter_count: int = Field(default=0, description="Number of valid parameters processed.")
    missing_parameters: List[str] = Field(default_factory=list, description="Parameters expected but missing.")
    unexpected_parameters: List[str] = Field(default_factory=list, description="Parameters present but not expected.")
    shape_mismatches: List[str] = Field(default_factory=list, description="Parameters with mismatched tensor shapes.")

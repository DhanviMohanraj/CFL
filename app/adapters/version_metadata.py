"""DriftAdapt Adapter Version Metadata.

Author: DriftAdapt Contributors
Purpose: Defines the immutable schema for an adapter version.
"""

import re
import time
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class AdapterVersionMetadata(BaseModel):
    """Immutable metadata record of a specific adapter version."""
    
    version_id: str = Field(..., description="Globally unique identifier e.g., clinic_001_round_0001_v1")
    adapter_id: str = Field(..., description="The base adapter ID this version belongs to.")
    clinic_id: str = Field(..., description="Clinic that produced this version.")
    communication_round: int = Field(..., description="The federated round when this was produced.")
    local_training_round: int = Field(..., description="The local epoch/round.")
    version_number: int = Field(..., description="Sequential version number for this clinic/adapter.")
    parent_version: Optional[str] = Field(None, description="The version_id this was trained from.")
    created_at: float = Field(default_factory=time.time, description="POSIX timestamp.")
    created_by: str = Field("system", description="Entity that created the version.")
    checksum: str = Field(..., description="SHA256 checksum of the weights.")
    parameter_count: int = Field(..., description="Total scalar parameters.")
    adapter_size_bytes: int = Field(..., description="Size in bytes.")
    serialization_format: str = Field("torch", description="Format used to save.")
    notes: Optional[str] = Field(None, description="Optional text notes.")
    tags: List[str] = Field(default_factory=list, description="Tags for searching.")
    status: str = Field("CREATED", description="The lifecycle status of this version.")

    @field_validator("version_id")
    @classmethod
    def validate_version_id(cls, v: str) -> str:
        """Ensures version_id follows the <clinic>_round_<num>_v<num> convention."""
        if not re.match(r"^.+_round_\d+_v\d+$", v):
            raise ValueError(f"version_id {v} does not match expected format <clinic>_round_<num>_v<num>")
        return v

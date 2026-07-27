"""DriftAdapt Adapter Merge Metadata.

Author: DriftAdapt Contributors
Purpose: Defines the schema for metadata emitted after a merge operation.
"""

import time
from typing import List, Optional

from pydantic import BaseModel, Field


class AdapterMergeMetadata(BaseModel):
    """Immutable metadata record of a merge operation."""
    
    merge_id: str = Field(..., description="Globally unique identifier for this merge event.")
    merge_timestamp: float = Field(default_factory=time.time, description="POSIX timestamp of merge.")
    strategy: str = Field(..., description="The name of the merge strategy used.")
    participating_clinics: List[str] = Field(..., description="List of clinic IDs that contributed.")
    participating_versions: List[str] = Field(..., description="List of version IDs merged.")
    parameter_count: int = Field(..., description="Parameters per input adapter.")
    merged_parameter_count: int = Field(..., description="Parameters in output adapter.")
    communication_round: int = Field(..., description="The federated round of this merge.")
    checksum: str = Field(..., description="Checksum of the resulting merged weights.")
    merge_duration_ms: float = Field(..., description="Duration of the merge computation.")
    output_adapter_id: str = Field(..., description="The ID assigned to the new adapter.")
    notes: Optional[str] = Field(None, description="Optional text notes.")

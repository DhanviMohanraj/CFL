"""Adapter Selection Schema.

Author: DriftAdapt Contributors
Purpose: Represents metadata of an adapter selected for an inference run.
"""

from typing import Optional
from pydantic import BaseModel, Field
import time


class AdapterSelection(BaseModel):
    """Metadata surrounding the active adapter chosen for a request."""
    
    adapter_id: str = Field(..., description="Unique identifier for the adapter (e.g. 'hospital-a')")
    adapter_name: str = Field(..., description="Human-readable name")
    adapter_version: str = Field(default="latest", description="Version string")
    adapter_status: str = Field(default="LOADED", description="Status (e.g., LOADED, CACHED, ACTIVE)")
    load_timestamp: float = Field(default_factory=time.time, description="Unix timestamp when this adapter was loaded into memory")
    priority: int = Field(default=0, description="Priority for cache eviction or conflict resolution")

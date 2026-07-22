"""DriftAdapt Adapter Metadata Schema.

Author: DriftAdapt Contributors
Purpose: Pydantic schema for returning stored adapter metadata from the registry.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AdapterMetadataResponse(BaseModel):
    """API response model detailing an initialized adapter."""

    adapter_id: str = Field(..., description="Internal registry ID for the adapter.")
    adapter_name: str = Field(..., description="Human-readable name of the adapter.")
    creation_timestamp: str = Field(..., description="ISO-8601 timestamp of initialization.")
    model_name: str = Field(..., description="Name of the foundation model this adapter targets.")
    
    parameter_count: int = Field(..., description="Total parameters in the model.")
    trainable_parameters: int = Field(..., description="Trainable parameters after injection.")
    frozen_parameters: int = Field(..., description="Frozen parameters in the base model.")
    
    adapter_rank: int = Field(..., description="Rank (r) used for this adapter.")
    adapter_alpha: float = Field(..., description="Alpha scaling factor used.")
    adapter_dropout: float = Field(..., description="Dropout rate used.")
    adapter_version: str = Field("1.0", description="Version of the adapter.")
    
    target_modules: List[str] = Field(default_factory=list, description="Target modules injected.")

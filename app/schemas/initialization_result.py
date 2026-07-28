"""DriftAdapt Initialization Result Schema.

Author: DriftAdapt Contributors
Purpose: Pydantic schema for returning the result of adapter initialization.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class InitializationResultResponse(BaseModel):
    """API response model summarizing the result of a PEFT injection."""

    success: bool = Field(..., description="Whether initialization was successful.")
    adapter_loaded: bool = Field(..., description="Whether the adapter was loaded into the model.")
    validation_status: str = Field(..., description="Status of invariants (e.g. 'PASSED').")
    
    configuration_summary: Dict[str, Any] = Field(..., description="Summary of the applied configuration.")
    warnings: List[str] = Field(default_factory=list, description="Any warnings encountered.")
    initialization_time_ms: float = Field(..., description="Time taken to initialize in milliseconds.")
    
    adapter_id: Optional[str] = Field(None, description="The ID of the registered adapter if successful.")

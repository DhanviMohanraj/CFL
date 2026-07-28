"""DriftAdapt Aggregation Schema.

Author: DriftAdapt Contributors
"""

import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AggregationMetadata(BaseModel):
    """Metadata regarding an aggregation event."""
    round_id: str = Field(..., description="Unique ID for the round.")
    algorithm: str = Field(..., description="The algorithm used for aggregation.")
    participating_clinics: List[str] = Field(..., description="Clinics that provided adapters.")
    start_time: float = Field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: Optional[float] = None
    status: str = Field(default="CREATED", description="Current status of the aggregation.")
    global_adapter_version: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Aggregation metrics.")
    checksum: Optional[str] = None

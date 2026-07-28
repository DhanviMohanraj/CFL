"""DriftAdapt Execution Schema.

Author: DriftAdapt Contributors
"""

import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class RoundMetadata(BaseModel):
    """Metadata regarding a federated execution round."""
    round_id: str = Field(..., description="Unique ID for the round.")
    month: int = Field(..., description="The simulated month.")
    epoch: int = Field(default=0, description="The current epoch.")
    participating_clinics: List[str] = Field(default_factory=list, description="Clinics in this round.")
    start_time: float = Field(default_factory=time.time)
    end_time: Optional[float] = None
    status: str = Field(default="CREATED", description="Current status of the round.")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Execution metrics.")

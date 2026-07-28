"""DriftAdapt Experiment Schema.

Author: DriftAdapt Contributors
"""

import time
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field


class ExperimentMetadata(BaseModel):
    """Metadata regarding a federated experiment."""
    experiment_id: str = Field(..., description="Unique ID for the experiment.")
    name: str = Field(..., description="Name of the experiment.")
    start_time: float = Field(default_factory=time.time)
    end_time: Optional[float] = None
    status: str = Field(default="CREATED", description="Current status of the experiment.")
    current_month: int = Field(default=1, description="Current simulated month.")
    completed_rounds: int = Field(default=0, description="Number of completed communication rounds.")
    config: Dict[str, Any] = Field(default_factory=dict, description="Experiment configuration.")


class ClinicAllocation(BaseModel):
    """Metadata regarding clinic assignments."""
    clinic_id: str
    month: int
    dataset_path: str
    is_active: bool = True

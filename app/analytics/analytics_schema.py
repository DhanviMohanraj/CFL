"""DriftAdapt Analytics Schema.

Author: DriftAdapt Contributors
"""

import time
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AnalyticsRecord(BaseModel):
    """Represents a generated analytics record."""
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    
    # Metadata
    round_id: int
    experiment_id: str
    
    # Generated outputs
    generated_reports: List[str] = Field(default_factory=list)
    generated_visualizations: List[str] = Field(default_factory=list)
    generated_dashboards: List[str] = Field(default_factory=list)

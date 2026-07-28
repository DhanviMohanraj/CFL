"""DriftAdapt Adaptive Schema.

Author: DriftAdapt Contributors
"""

import time
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AdaptiveRecord(BaseModel):
    """Represents an adaptive aggregation record."""
    adaptation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    
    # Inputs
    decision_id: str
    participating_clinics: List[str]
    
    # Decisions
    strategy_name: str
    weights: Dict[str, float] = Field(default_factory=dict)
    clusters: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Outcomes
    aggregated_adapter_path: Optional[str] = None
    redistribution_plan: Dict[str, Any] = Field(default_factory=dict)
    effectiveness_metrics: Dict[str, Any] = Field(default_factory=dict)

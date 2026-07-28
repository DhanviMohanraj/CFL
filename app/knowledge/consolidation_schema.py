"""DriftAdapt Knowledge Consolidation Schema.

Author: DriftAdapt Contributors
"""

import time
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ConsolidationRecord(BaseModel):
    """Represents a knowledge consolidation record."""
    consolidation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    
    # Inputs
    round_id: int
    adaptive_global_adapter_path: str
    
    # Decisions
    strategy_name: str
    privacy_applied: bool = False
    
    # Metrics
    forgetting_score: Optional[float] = None
    retention_score: Optional[float] = None
    privacy_epsilon: Optional[float] = None
    privacy_delta: Optional[float] = None
    svd_rank: Optional[int] = None
    
    # Outputs
    consolidated_adapter_path: Optional[str] = None

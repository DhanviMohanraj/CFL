"""DriftAdapt Evaluation Schema.

Author: DriftAdapt Contributors
"""

import time
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class EvaluationRecord(BaseModel):
    """Represents a generated evaluation record."""
    evaluation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    
    # Metadata
    experiment_id: str
    algorithms_compared: List[str] = Field(default_factory=list)
    benchmarks_run: List[str] = Field(default_factory=list)

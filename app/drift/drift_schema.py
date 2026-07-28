"""DriftAdapt Drift Schema.

Author: DriftAdapt Contributors
"""

import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class FeatureDriftScore(BaseModel):
    feature_name: str
    detector: str
    score: float
    is_drift: bool
    threshold: float
    details: Dict[str, Any] = Field(default_factory=dict)


class DriftReport(BaseModel):
    clinic_id: str
    month: int
    baseline_month: int
    timestamp: float = Field(default_factory=time.time)
    
    # Feature drift
    feature_scores: List[FeatureDriftScore] = Field(default_factory=list)
    overall_psi: Optional[float] = None
    
    # Classification
    drift_detected: bool = False
    drift_type: str = "NONE" # e.g., COVARIATE, LABEL, CONCEPT, TEMPORAL
    severity: str = "NONE"   # e.g., LOW, MODERATE, SIGNIFICANT
    
    # Metadata
    metrics: Dict[str, Any] = Field(default_factory=dict)

"""DriftAdapt Concept Drift Detector.

Author: DriftAdapt Contributors
"""

import pandas as pd
from typing import Dict, Any, List

from app.drift.analyzers.base_detector import BaseDetector
from app.drift.drift_schema import FeatureDriftScore


class ConceptDetector(BaseDetector):
    """Detects concept drift (relationship changes)."""
    
    def detect(self, reference: pd.DataFrame, current: pd.DataFrame, config: Dict[str, Any]) -> List[FeatureDriftScore]:
        # Concept drift usually involves joint distributions P(X, Y)
        # We leave this extensible for future ML-based approaches.
        return []

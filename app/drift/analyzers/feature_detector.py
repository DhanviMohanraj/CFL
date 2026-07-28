"""DriftAdapt Feature Drift Detector.

Author: DriftAdapt Contributors
"""

import pandas as pd
from typing import Dict, Any, List

from app.drift.analyzers.base_detector import BaseDetector
from app.drift.drift_schema import FeatureDriftScore
from app.drift.analyzers.psi_detector import PSIDetector
from app.drift.analyzers.chi_square_detector import ChiSquareDetector


class FeatureDetector(BaseDetector):
    """Detects drift for all features using combined metrics."""
    
    def __init__(self) -> None:
        self.num_detector = PSIDetector()
        self.cat_detector = ChiSquareDetector()
        
    def detect(self, reference: pd.DataFrame, current: pd.DataFrame, config: Dict[str, Any]) -> List[FeatureDriftScore]:
        scores = []
        scores.extend(self.num_detector.detect(reference, current, config))
        scores.extend(self.cat_detector.detect(reference, current, config))
        return scores

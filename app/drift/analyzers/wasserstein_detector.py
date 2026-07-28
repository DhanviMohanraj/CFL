"""DriftAdapt Wasserstein Drift Detector.

Author: DriftAdapt Contributors
"""

import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance
from typing import Dict, Any, List

from app.drift.analyzers.base_detector import BaseDetector
from app.drift.drift_schema import FeatureDriftScore


class WassersteinDetector(BaseDetector):
    """Wasserstein (Earth Mover's) Distance drift detector."""
    
    def detect(self, reference: pd.DataFrame, current: pd.DataFrame, config: Dict[str, Any]) -> List[FeatureDriftScore]:
        threshold = config.get("wasserstein_threshold", 0.10)
        scores = []
        
        for col in reference.select_dtypes(include=[np.number]).columns:
            if col not in current.columns:
                continue
                
            ref_data = reference[col].dropna()
            cur_data = current[col].dropna()
            
            if len(ref_data) == 0 or len(cur_data) == 0:
                continue
                
            dist = wasserstein_distance(ref_data, cur_data)
            
            scores.append(FeatureDriftScore(
                feature_name=col,
                detector="WASSERSTEIN",
                score=float(dist),
                is_drift=dist > threshold,
                threshold=threshold
            ))
            
        return scores

"""DriftAdapt PSI Drift Detector.

Author: DriftAdapt Contributors
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List

from app.drift.analyzers.base_detector import BaseDetector
from app.drift.drift_schema import FeatureDriftScore


class PSIDetector(BaseDetector):
    """Population Stability Index (PSI) drift detector."""
    
    def detect(self, reference: pd.DataFrame, current: pd.DataFrame, config: Dict[str, Any]) -> List[FeatureDriftScore]:
        threshold = config.get("psi_threshold", 0.25)
        scores = []
        
        for col in reference.select_dtypes(include=[np.number]).columns:
            if col not in current.columns:
                continue
                
            ref_data = reference[col].dropna()
            cur_data = current[col].dropna()
            
            if len(ref_data) == 0 or len(cur_data) == 0:
                continue
                
            # Create common bins
            min_val = min(ref_data.min(), cur_data.min())
            max_val = max(ref_data.max(), cur_data.max())
            if min_val == max_val:
                continue
            
            # 10 bins
            bins = np.linspace(min_val, max_val, 11)
            
            ref_counts, _ = np.histogram(ref_data, bins=bins)
            cur_counts, _ = np.histogram(cur_data, bins=bins)
            
            # To probabilities
            ref_prob = ref_counts / len(ref_data)
            cur_prob = cur_counts / len(cur_data)
            
            # Avoid division by zero
            epsilon = 1e-4
            ref_prob = np.where(ref_prob == 0, epsilon, ref_prob)
            cur_prob = np.where(cur_prob == 0, epsilon, cur_prob)
            
            psi_val = np.sum((cur_prob - ref_prob) * np.log(cur_prob / ref_prob))
            
            scores.append(FeatureDriftScore(
                feature_name=col,
                detector="PSI",
                score=float(psi_val),
                is_drift=psi_val > threshold,
                threshold=threshold
            ))
            
        return scores

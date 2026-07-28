"""DriftAdapt JS Divergence Drift Detector.

Author: DriftAdapt Contributors
"""

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from typing import Dict, Any, List

from app.drift.analyzers.base_detector import BaseDetector
from app.drift.drift_schema import FeatureDriftScore


class JSDetector(BaseDetector):
    """Jensen-Shannon Divergence drift detector."""
    
    def detect(self, reference: pd.DataFrame, current: pd.DataFrame, config: Dict[str, Any]) -> List[FeatureDriftScore]:
        threshold = config.get("js_threshold", 0.20)
        scores = []
        
        for col in reference.columns:
            if col not in current.columns:
                continue
                
            ref_data = reference[col].dropna()
            cur_data = current[col].dropna()
            
            if len(ref_data) == 0 or len(cur_data) == 0:
                continue
                
            if pd.api.types.is_numeric_dtype(ref_data):
                min_val = min(ref_data.min(), cur_data.min())
                max_val = max(ref_data.max(), cur_data.max())
                if min_val == max_val:
                    continue
                bins = np.linspace(min_val, max_val, 11)
                
                ref_counts, _ = np.histogram(ref_data, bins=bins)
                cur_counts, _ = np.histogram(cur_data, bins=bins)
                
                ref_prob = ref_counts / len(ref_data)
                cur_prob = cur_counts / len(cur_data)
            else:
                all_cats = set(ref_data.unique()).union(set(cur_data.unique()))
                ref_counts = ref_data.value_counts().reindex(list(all_cats), fill_value=0)
                cur_counts = cur_data.value_counts().reindex(list(all_cats), fill_value=0)
                
                ref_prob = ref_counts.values / len(ref_data)
                cur_prob = cur_counts.values / len(cur_data)
                
            js_dist = jensenshannon(ref_prob, cur_prob)
            
            scores.append(FeatureDriftScore(
                feature_name=col,
                detector="JS",
                score=float(js_dist),
                is_drift=js_dist > threshold,
                threshold=threshold
            ))
            
        return scores

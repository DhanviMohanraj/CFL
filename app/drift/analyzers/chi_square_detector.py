"""DriftAdapt Chi-Square Drift Detector.

Author: DriftAdapt Contributors
"""

import pandas as pd
from scipy.stats import chi2_contingency
from typing import Dict, Any, List

from app.drift.analyzers.base_detector import BaseDetector
from app.drift.drift_schema import FeatureDriftScore


class ChiSquareDetector(BaseDetector):
    """Chi-square drift detector for categorical features."""
    
    def detect(self, reference: pd.DataFrame, current: pd.DataFrame, config: Dict[str, Any]) -> List[FeatureDriftScore]:
        alpha = config.get("chi_square_alpha", 0.05)
        scores = []
        
        for col in reference.select_dtypes(exclude=['number']).columns:
            if col not in current.columns:
                continue
                
            ref_data = reference[col].dropna()
            cur_data = current[col].dropna()
            
            if len(ref_data) == 0 or len(cur_data) == 0:
                continue
                
            all_cats = set(ref_data.unique()).union(set(cur_data.unique()))
            if len(all_cats) <= 1:
                continue
                
            ref_counts = ref_data.value_counts().reindex(list(all_cats), fill_value=0)
            cur_counts = cur_data.value_counts().reindex(list(all_cats), fill_value=0)
            
            # Avoid zeroes for chi-square
            ref_counts = ref_counts + 1
            cur_counts = cur_counts + 1
            
            # Create contingency table
            table = [ref_counts.values, cur_counts.values]
            
            try:
                _, p_val, _, _ = chi2_contingency(table)
                is_drift = p_val < alpha
                
                scores.append(FeatureDriftScore(
                    feature_name=col,
                    detector="CHI_SQUARE",
                    score=float(p_val),
                    is_drift=is_drift,
                    threshold=alpha
                ))
            except Exception:
                pass
                
        return scores

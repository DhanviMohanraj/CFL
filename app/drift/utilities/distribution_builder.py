"""DriftAdapt Distribution Builder.

Author: DriftAdapt Contributors
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


class DistributionBuilder:
    """Builds distributions from datasets for drift analysis."""
    
    @staticmethod
    def build_distributions(reference: pd.Series, current: pd.Series) -> tuple:
        """Returns normalized probability distributions for a given feature."""
        if pd.api.types.is_numeric_dtype(reference):
            min_val = min(reference.min(), current.min())
            max_val = max(reference.max(), current.max())
            if min_val == max_val:
                return np.array([1.0]), np.array([1.0])
                
            bins = np.linspace(min_val, max_val, 11)
            ref_counts, _ = np.histogram(reference.dropna(), bins=bins)
            cur_counts, _ = np.histogram(current.dropna(), bins=bins)
            
            ref_prob = ref_counts / len(reference.dropna())
            cur_prob = cur_counts / len(current.dropna())
            
        else:
            all_cats = set(reference.dropna().unique()).union(set(current.dropna().unique()))
            ref_counts = reference.value_counts().reindex(list(all_cats), fill_value=0)
            cur_counts = current.value_counts().reindex(list(all_cats), fill_value=0)
            
            ref_prob = ref_counts.values / len(reference.dropna())
            cur_prob = cur_counts.values / len(current.dropna())
            
        return ref_prob, cur_prob

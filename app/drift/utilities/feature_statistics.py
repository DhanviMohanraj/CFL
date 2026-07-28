"""DriftAdapt Feature Statistics.

Author: DriftAdapt Contributors
"""

import pandas as pd
from typing import Dict, Any


class FeatureStatistics:
    """Computes basic statistics for features to aid in drift analysis."""
    
    @staticmethod
    def compute(data: pd.Series) -> Dict[str, Any]:
        """Computes summary statistics for a feature."""
        stats = {
            "missing_count": int(data.isna().sum()),
            "missing_percentage": float(data.isna().mean()),
            "unique_values": int(data.nunique())
        }
        
        if pd.api.types.is_numeric_dtype(data):
            stats.update({
                "mean": float(data.mean()) if not data.isna().all() else 0.0,
                "std": float(data.std()) if not data.isna().all() else 0.0,
                "min": float(data.min()) if not data.isna().all() else 0.0,
                "max": float(data.max()) if not data.isna().all() else 0.0
            })
            
        return stats

"""DriftAdapt Histogram Builder.

Author: DriftAdapt Contributors
"""

import numpy as np
import pandas as pd


class HistogramBuilder:
    """Builds histograms for visualizing and comparing drift."""
    
    @staticmethod
    def build(data: pd.Series, bins: int = 10) -> tuple:
        """Builds a histogram for a numeric feature."""
        if not pd.api.types.is_numeric_dtype(data):
            raise ValueError("HistogramBuilder requires numeric data.")
            
        data = data.dropna()
        if data.empty:
            return np.array([]), np.array([])
        counts, bin_edges = np.histogram(data, bins=bins)
        return counts, bin_edges

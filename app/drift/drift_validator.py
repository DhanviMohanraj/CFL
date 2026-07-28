"""DriftAdapt Drift Validator.

Author: DriftAdapt Contributors
"""

import pandas as pd
from typing import Any

from app.drift.drift_exceptions import DatasetComparisonError


class DriftValidator:
    """Validates datasets before drift analysis."""
    
    def validate_datasets(self, reference: pd.DataFrame, current: pd.DataFrame) -> None:
        """Validates that two dataframes can be compared."""
        if reference.empty:
            raise DatasetComparisonError("Reference dataset is empty.")
            
        if current.empty:
            raise DatasetComparisonError("Current dataset is empty.")
            
        ref_cols = set(reference.columns)
        cur_cols = set(current.columns)
        
        if not ref_cols.intersection(cur_cols):
            raise DatasetComparisonError("No overlapping features between reference and current datasets.")

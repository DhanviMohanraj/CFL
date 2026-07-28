"""Tests for Drift Validator.

Author: DriftAdapt Contributors
"""

import pandas as pd
import pytest
from app.drift.drift_validator import DriftValidator
from app.drift.drift_exceptions import DatasetComparisonError


def test_drift_validator():
    validator = DriftValidator()
    
    df1 = pd.DataFrame({"a": [1]})
    df2 = pd.DataFrame({"b": [2]})
    df_empty = pd.DataFrame()
    
    with pytest.raises(DatasetComparisonError):
        validator.validate_datasets(df_empty, df1)
        
    with pytest.raises(DatasetComparisonError):
        validator.validate_datasets(df1, df2)
        
    validator.validate_datasets(df1, df1) # Should pass

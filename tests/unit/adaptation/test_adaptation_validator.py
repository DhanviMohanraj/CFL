"""Tests for Adaptation Validator.

Author: DriftAdapt Contributors
"""

import pytest
from app.adaptation.adaptation_validator import AdaptationValidator
from app.adaptation.adaptation_exceptions import ValidationError
from app.drift.drift_schema import DriftReport


def test_adaptation_validator():
    validator = AdaptationValidator()
    
    with pytest.raises(ValidationError):
        validator.validate_reports([])
        
    report = DriftReport(clinic_id="c1", month=1, baseline_month=0)
    validator.validate_reports([report]) # Should pass

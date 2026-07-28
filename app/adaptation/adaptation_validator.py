"""DriftAdapt Adaptation Validator.

Author: DriftAdapt Contributors
"""

from typing import List, Any
from app.drift.drift_schema import DriftReport
from app.adaptation.adaptation_exceptions import ValidationError


class AdaptationValidator:
    """Validates inputs and outputs of the adaptation engine."""
    
    def validate_reports(self, reports: List[DriftReport]) -> None:
        """Validates incoming drift reports."""
        if not reports:
            raise ValidationError("Cannot evaluate adaptation without drift reports.")
            
        for report in reports:
            if not hasattr(report, "clinic_id") or not hasattr(report, "drift_detected"):
                raise ValidationError("Invalid drift report schema.")

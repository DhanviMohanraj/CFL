"""DriftAdapt Clinic Selector.

Author: DriftAdapt Contributors
"""

from typing import List
from app.drift.drift_schema import DriftReport


class ClinicSelector:
    """Selects clinics that require adaptation based on drift reports."""
    
    @staticmethod
    def get_affected_clinics(reports: List[DriftReport]) -> List[str]:
        """Returns a list of clinic IDs showing any drift."""
        return [r.clinic_id for r in reports if r.drift_detected]
        
    @staticmethod
    def get_severe_clinics(reports: List[DriftReport]) -> List[str]:
        """Returns a list of clinic IDs showing significant drift."""
        return [r.clinic_id for r in reports if r.severity == "SIGNIFICANT"]

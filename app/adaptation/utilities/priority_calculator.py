"""DriftAdapt Priority Calculator.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, List
from app.drift.drift_schema import DriftReport
from app.adaptation.adaptation_priority import PriorityLevel


class PriorityCalculator:
    """Calculates priority scores based on severity and affected population."""
    
    @staticmethod
    def calculate(reports: List[DriftReport], config: Dict[str, Any]) -> str:
        """Computes priority level."""
        if not reports:
            return PriorityLevel.LOW
            
        severe = sum(1 for r in reports if r.severity == "SIGNIFICANT")
        moderate = sum(1 for r in reports if r.severity == "MODERATE")
        
        if severe > 0:
            if severe >= config.get("global_clinic_threshold", 3):
                return PriorityLevel.CRITICAL
            return PriorityLevel.HIGH
        elif moderate > 0:
            return PriorityLevel.MEDIUM
        return PriorityLevel.LOW

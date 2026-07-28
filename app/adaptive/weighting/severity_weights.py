"""DriftAdapt Severity Weights.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, List
from app.drift.drift_schema import DriftReport


class SeverityWeights:
    """Calculates weights based on drift severity."""
    
    @staticmethod
    def calculate(reports: List[DriftReport], config: Dict[str, Any]) -> Dict[str, float]:
        weights = {}
        for r in reports:
            if r.severity == "SIGNIFICANT":
                weights[r.clinic_id] = 0.5
            elif r.severity == "MODERATE":
                weights[r.clinic_id] = 0.3
            else:
                weights[r.clinic_id] = 0.2
                
        total = sum(weights.values())
        if total > 0:
            return {k: v / total for k, v in weights.items()}
        return {k: 1.0 / len(weights) for k in weights} if weights else {}

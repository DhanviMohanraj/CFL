"""DriftAdapt Confidence Weights.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, List


class ConfidenceWeights:
    """Calculates weights based on adaptation decision confidence."""
    
    @staticmethod
    def calculate(clinics: List[str], confidence: float, config: Dict[str, Any]) -> Dict[str, float]:
        if not clinics:
            return {}
        return {c: 1.0 / len(clinics) for c in clinics}

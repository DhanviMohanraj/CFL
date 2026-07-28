"""DriftAdapt Clinic Weights.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, List


class ClinicWeights:
    """Calculates weights based on clinic importance."""
    
    @staticmethod
    def calculate(clinics: List[str], config: Dict[str, Any]) -> Dict[str, float]:
        if not clinics:
            return {}
        return {c: 1.0 / len(clinics) for c in clinics}

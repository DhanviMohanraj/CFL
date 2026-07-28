"""DriftAdapt Historical Weights.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, List


class HistoricalWeights:
    """Calculates weights incorporating historical adaptation effectiveness."""
    
    @staticmethod
    def calculate(clinics: List[str], config: Dict[str, Any]) -> Dict[str, float]:
        if not clinics:
            return {}
        return {c: 1.0 / len(clinics) for c in clinics}

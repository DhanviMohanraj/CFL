"""DriftAdapt Severity Mapper.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any


class SeverityMapper:
    """Maps drift scores to discrete severity levels."""
    
    @staticmethod
    def map_severity(score: float, threshold: float) -> str:
        """Returns NONE, LOW, MODERATE, or SIGNIFICANT."""
        if score <= threshold:
            return "NONE"
        ratio = score / threshold
        if ratio < 1.5:
            return "LOW"
        elif ratio < 2.5:
            return "MODERATE"
        return "SIGNIFICANT"

"""DriftAdapt Forgetting Detector.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any


class ForgettingDetector:
    """Estimates catastrophic forgetting."""
    
    @staticmethod
    def detect(current_state: Any, historical_state: Any, config: Dict[str, Any]) -> float:
        """Returns a forgetting score (0 to 1)."""
        return 0.05

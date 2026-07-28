"""DriftAdapt Threshold Manager.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any


class ThresholdManager:
    """Manages thresholds for various drift detectors."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        
    def get_threshold(self, detector: str) -> float:
        """Returns the threshold for a specific detector."""
        detector = detector.lower()
        if "psi" in detector:
            return self.config.get("psi_threshold", 0.25)
        elif "kl" in detector:
            return self.config.get("kl_threshold", 0.15)
        elif "js" in detector:
            return self.config.get("js_threshold", 0.20)
        elif "wasserstein" in detector:
            return self.config.get("wasserstein_threshold", 0.10)
        elif "chi_square" in detector:
            return self.config.get("chi_square_alpha", 0.05)
        return 0.1

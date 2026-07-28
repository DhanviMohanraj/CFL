"""DriftAdapt Drift Analyzer.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, List
import pandas as pd

from app.drift.drift_schema import DriftReport, FeatureDriftScore


class DriftAnalyzer:
    """Orchestrates multiple detectors for a dataset comparison."""
    
    def __init__(self, detectors: List[Any]) -> None:
        self.detectors = detectors
        
    def analyze(self, reference: pd.DataFrame, current: pd.DataFrame, config: Dict[str, Any]) -> List[FeatureDriftScore]:
        """Runs all configured detectors and aggregates scores."""
        all_scores = []
        for detector in self.detectors:
            scores = detector.detect(reference, current, config)
            all_scores.extend(scores)
        return all_scores

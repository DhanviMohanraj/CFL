"""DriftAdapt Base Drift Detector.

Author: DriftAdapt Contributors
"""

import abc
import pandas as pd
from typing import Dict, Any, List
from app.drift.drift_schema import FeatureDriftScore


class BaseDetector(abc.ABC):
    """Abstract base class for all drift detectors."""
    
    @abc.abstractmethod
    def detect(self, reference: pd.DataFrame, current: pd.DataFrame, config: Dict[str, Any]) -> List[FeatureDriftScore]:
        """Detects drift between a reference and current dataset."""
        pass

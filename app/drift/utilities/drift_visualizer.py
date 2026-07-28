"""DriftAdapt Drift Visualizer.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any
from app.drift.drift_schema import DriftReport


class DriftVisualizer:
    """Placeholder for drift visualization utilities."""
    
    @staticmethod
    def generate_drift_dashboard(report: DriftReport) -> Dict[str, Any]:
        """Generates a summary structure suitable for a UI dashboard."""
        return {
            "clinic": report.clinic_id,
            "month": report.month,
            "drift_detected": report.drift_detected,
            "severity": report.severity,
            "drifting_features": [f.feature_name for f in report.feature_scores if f.is_drift]
        }

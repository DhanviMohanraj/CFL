"""DriftAdapt Drift Reporter.

Author: DriftAdapt Contributors
"""

import json
from typing import Dict, Any, List
from app.drift.drift_schema import DriftReport


class DriftReporter:
    """Generates formatted reports from drift detection."""
    
    def generate_json(self, report: DriftReport) -> str:
        """Returns JSON representation of a drift report."""
        return report.model_dump_json(indent=2)
        
    def generate_summary(self, reports: List[DriftReport]) -> Dict[str, Any]:
        """Generates an aggregate summary over multiple reports."""
        drifts = [r for r in reports if r.drift_detected]
        return {
            "total_analyzed": len(reports),
            "total_drift_detected": len(drifts),
            "clinics_with_drift": list(set(r.clinic_id for r in drifts))
        }

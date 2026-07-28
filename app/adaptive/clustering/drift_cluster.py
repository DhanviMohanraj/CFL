"""DriftAdapt Drift Cluster.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any
from app.drift.drift_schema import DriftReport


class DriftCluster:
    """Manages clusters of clinics with similar drift profiles."""
    
    @staticmethod
    def cluster(reports: List[DriftReport], config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Clusters clinics based on drift severity."""
        clusters = {"severe": [], "moderate": [], "low": [], "none": []}
        for r in reports:
            if r.severity == "SIGNIFICANT":
                clusters["severe"].append(r.clinic_id)
            elif r.severity == "MODERATE":
                clusters["moderate"].append(r.clinic_id)
            elif r.drift_detected:
                clusters["low"].append(r.clinic_id)
            else:
                clusters["none"].append(r.clinic_id)
                
        # Remove empty clusters
        return {k: v for k, v in clusters.items() if v}

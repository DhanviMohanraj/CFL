"""DriftAdapt Dashboards Module.

Author: DriftAdapt Contributors
"""

from app.analytics.dashboards.federated_dashboard import FederatedDashboard
from app.analytics.dashboards.clinic_dashboard import ClinicDashboard
from app.analytics.dashboards.drift_dashboard import DriftDashboard
from app.analytics.dashboards.adaptation_dashboard import AdaptationDashboard
from app.analytics.dashboards.privacy_dashboard import PrivacyDashboard
from app.analytics.dashboards.research_dashboard import ResearchDashboard

__all__ = [
    "FederatedDashboard",
    "ClinicDashboard",
    "DriftDashboard",
    "AdaptationDashboard",
    "PrivacyDashboard",
    "ResearchDashboard"
]

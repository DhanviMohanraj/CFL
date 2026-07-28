"""Tests for Dashboards.

Author: DriftAdapt Contributors
"""

from app.analytics.dashboards.federated_dashboard import FederatedDashboard


def test_federated_dashboard():
    dashboard = FederatedDashboard()
    assert dashboard is not None

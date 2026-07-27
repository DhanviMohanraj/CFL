"""Tests for Timeout Manager.

Author: DriftAdapt Contributors
"""

import pytest

from app.federated.coordinator.timeout_manager import TimeoutManager
from app.federated.coordinator.coordinator_metrics import CoordinatorMetrics
from app.core.metrics.metrics_bus import MetricsBus
from app.federated.coordinator.coordinator_exceptions import SynchronizationTimeout


def test_timeout_manager():
    bus = MetricsBus()
    metrics = CoordinatorMetrics(bus)
    manager = TimeoutManager(metrics, upload_timeout=10.0)
    
    # Should not raise
    manager.check_synchronization_timeout(5.0, 10.0)
    
    # Should raise
    with pytest.raises(SynchronizationTimeout):
        manager.check_synchronization_timeout(15.0, 10.0)
        
    manager.handle_upload_timeout("round_1", "client_1")

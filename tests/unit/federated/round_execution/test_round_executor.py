"""Tests for Round Executor.

Author: DriftAdapt Contributors
"""

import pytest
from app.core.metrics.metrics_bus import MetricsBus
from app.federated.round_execution.round_executor import FederatedRoundExecutor
from app.federated.round_execution.round_state_machine import RoundState


def test_round_executor():
    bus = MetricsBus()
    config = {
        "max_parallel_clients": 4,
        "client_timeout": 600,
        "checkpoint_before_aggregation": False,
        "checkpoint_after_round": False
    }
    
    executor = FederatedRoundExecutor(config, bus)
    
    clients = ["clinic_01", "clinic_02"]
    
    round_id = executor.initialize(month=1, epoch=1, clients=clients)
    assert round_id is not None
    assert executor.status() == RoundState.PREPARING.value
    
    executor.execute(clients, month=1)
    
    assert executor.status() == RoundState.COMPLETED.value

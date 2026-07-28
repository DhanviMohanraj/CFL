"""Tests for Aggregation Trigger.

Author: DriftAdapt Contributors
"""

import pytest
from app.federated.round_execution.aggregation_trigger import AggregationTrigger
from app.federated.round_execution.execution_exceptions import AggregationTriggerError


def test_aggregation_trigger():
    trigger = AggregationTrigger()
    
    path = trigger.trigger_aggregation("r1", ["a1", "a2"])
    assert path == "exports/r1_global_adapter.pt"
    
    with pytest.raises(AggregationTriggerError):
        trigger.trigger_aggregation("r1", [])

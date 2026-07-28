"""Tests for Aggregation Factory.

Author: DriftAdapt Contributors
"""

import pytest
from app.aggregation.aggregation_factory import AggregationFactory
from app.aggregation.algorithms.fedavg import FedAvg
from app.aggregation.algorithms.weighted_fedavg import WeightedFedAvg
from app.aggregation.algorithms.fedprox import FedProx
from app.aggregation.algorithms.static_fedlora import StaticFedLoRA
from app.aggregation.algorithms.identity import IdentityAggregation
from app.aggregation.aggregation_exceptions import AlgorithmSelectionError


def test_aggregation_factory():
    assert isinstance(AggregationFactory.get_algorithm("fedavg"), FedAvg)
    assert isinstance(AggregationFactory.get_algorithm("weighted_fedavg"), WeightedFedAvg)
    assert isinstance(AggregationFactory.get_algorithm("fedprox"), FedProx)
    assert isinstance(AggregationFactory.get_algorithm("static_fedlora"), StaticFedLoRA)
    assert isinstance(AggregationFactory.get_algorithm("identity"), IdentityAggregation)
    
    with pytest.raises(AlgorithmSelectionError):
        AggregationFactory.get_algorithm("unknown")

"""Tests for Aggregation Algorithms.

Author: DriftAdapt Contributors
"""

import torch
import pytest
from app.aggregation.algorithms.fedavg import FedAvg
from app.aggregation.algorithms.weighted_fedavg import WeightedFedAvg
from app.aggregation.algorithms.fedprox import FedProx
from app.aggregation.algorithms.static_fedlora import StaticFedLoRA
from app.aggregation.algorithms.identity import IdentityAggregation
from app.aggregation.aggregation_exceptions import WeightedAggregationError


def test_fedavg():
    alg = FedAvg()
    sd1 = {"A": torch.tensor([1.0, 2.0]), "B": torch.tensor([3.0, 4.0])}
    sd2 = {"A": torch.tensor([3.0, 4.0]), "B": torch.tensor([5.0, 6.0])}
    
    res = alg.aggregate([sd1, sd2], [], {})
    assert torch.allclose(res["A"], torch.tensor([2.0, 3.0]))
    assert torch.allclose(res["B"], torch.tensor([4.0, 5.0]))


def test_weighted_fedavg():
    alg = WeightedFedAvg()
    sd1 = {"A": torch.tensor([1.0, 1.0])}
    sd2 = {"A": torch.tensor([4.0, 4.0])}
    
    meta1 = {"dataset_size": 100}
    meta2 = {"dataset_size": 200}
    
    res = alg.aggregate([sd1, sd2], [meta1, meta2], {})
    assert torch.allclose(res["A"], torch.tensor([3.0, 3.0]))
    
    with pytest.raises(WeightedAggregationError):
        alg.aggregate([sd1, sd2], [{"dataset_size": 0}, {"dataset_size": 0}], {})


def test_fedprox():
    alg = FedProx()
    sd1 = {"A": torch.tensor([1.0, 1.0])}
    sd2 = {"A": torch.tensor([4.0, 4.0])}
    meta = [{"dataset_size": 1.0}, {"dataset_size": 1.0}]
    
    res = alg.aggregate([sd1, sd2], meta, {})
    assert torch.allclose(res["A"], torch.tensor([2.5, 2.5]))


def test_static_fedlora():
    alg = StaticFedLoRA()
    sd1 = {"A": torch.tensor([1.0, 1.0])}
    sd2 = {"A": torch.tensor([3.0, 3.0])}
    
    res = alg.aggregate([sd1, sd2], [], {})
    assert torch.allclose(res["A"], torch.tensor([2.0, 2.0]))


def test_identity():
    alg = IdentityAggregation()
    sd1 = {"A": torch.tensor([1.0, 1.0])}
    sd2 = {"A": torch.tensor([3.0, 3.0])}
    
    res = alg.aggregate([sd1, sd2], [], {})
    assert torch.allclose(res["A"], torch.tensor([1.0, 1.0]))

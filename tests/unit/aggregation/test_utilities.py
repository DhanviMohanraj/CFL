"""Tests for Tensor Utilities.

Author: DriftAdapt Contributors
"""

import torch
import pytest
from app.aggregation.utilities.tensor_merger import average_tensors, weighted_average_tensors
from app.aggregation.utilities.tensor_validator import check_tensor_compatibility, detect_nans
from app.aggregation.utilities.tensor_statistics import compute_adapter_statistics
from app.aggregation.utilities.compatibility_checker import check_adapters_compatibility
from app.aggregation.utilities.adapter_normalizer import normalize_adapter


def test_average_tensors():
    t1 = torch.tensor([1.0, 2.0])
    t2 = torch.tensor([3.0, 4.0])
    res = average_tensors([t1, t2])
    assert torch.allclose(res, torch.tensor([2.0, 3.0]))


def test_weighted_average_tensors():
    t1 = torch.tensor([1.0])
    t2 = torch.tensor([4.0])
    res = weighted_average_tensors([t1, t2], [1.0, 2.0])
    assert torch.allclose(res, torch.tensor([3.0]))
    
    with pytest.raises(ValueError):
        weighted_average_tensors([t1], [1.0, 2.0])


def test_check_tensor_compatibility():
    t1 = torch.tensor([1.0, 2.0])
    t2 = torch.tensor([3.0, 4.0])
    t3 = torch.tensor([1.0])
    assert check_tensor_compatibility([t1, t2]) is True
    assert check_tensor_compatibility([t1, t3]) is False


def test_detect_nans():
    sd = {"A": torch.tensor([1.0, float("nan")])}
    assert detect_nans(sd) is True
    
    sd2 = {"A": torch.tensor([1.0, 2.0])}
    assert detect_nans(sd2) is False


def test_compute_adapter_statistics():
    sd = {"A": torch.randn(10, 10), "B": torch.randn(5)}
    stats = compute_adapter_statistics(sd)
    assert stats["total_parameters"] == 105
    assert stats["num_tensors"] == 2


def test_check_adapters_compatibility():
    sd1 = {"A": torch.randn(10), "B": torch.randn(5)}
    sd2 = {"A": torch.randn(10), "B": torch.randn(5)}
    sd3 = {"A": torch.randn(10)}
    assert check_adapters_compatibility([sd1, sd2]) is True
    assert check_adapters_compatibility([sd1, sd3]) is False


def test_normalize_adapter():
    sd = {"A": torch.tensor([3.0, 4.0])}
    res = normalize_adapter(sd)
    assert torch.allclose(res["A"], torch.tensor([0.6, 0.8]))

"""Tests for Aggregation Schema and Exceptions.

Author: DriftAdapt Contributors
"""

import pytest
from app.aggregation.aggregation_schema import AggregationMetadata
from app.aggregation.aggregation_exceptions import AggregationError


def test_aggregation_metadata():
    meta = AggregationMetadata(round_id="r1", algorithm="fedavg", participating_clinics=["c1"])
    assert meta.round_id == "r1"
    assert meta.status == "CREATED"

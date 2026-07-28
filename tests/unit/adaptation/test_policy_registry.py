"""Tests for Policy Registry and Factory.

Author: DriftAdapt Contributors
"""

import pytest
from app.adaptation.policy_registry import PolicyRegistry
from app.adaptation.policy_factory import PolicyFactory
from app.adaptation.adaptation_exceptions import PolicyEvaluationError


class MockPolicy:
    pass


def test_policy_registry():
    registry = PolicyRegistry()
    registry.register("mock", MockPolicy())
    assert registry.lookup("mock") is not None
    assert len(registry.all_policies()) == 1


def test_policy_factory():
    registry = PolicyRegistry()
    registry.register("mock", MockPolicy())
    factory = PolicyFactory(registry)
    
    assert factory.get_policy("mock") is not None
    
    with pytest.raises(PolicyEvaluationError):
        factory.get_policy("unknown")

"""Tests for Adapter Merge Strategy Interface.

Author: DriftAdapt Contributors
"""

import pytest

from typing import List, Dict, Any, Optional

from app.adapters.merge_strategy import AdapterMergeStrategy


class MockStrategy(AdapterMergeStrategy):
    """A mock implementation of the abstract strategy for testing."""
    
    def merge(self, states: List[Dict[str, Any]], weights: Optional[List[float]] = None) -> Dict[str, Any]:
        return {"merged": True}
        
    def validate_inputs(self, states: List[Dict[str, Any]]) -> None:
        pass
        
    def supports_weighting(self) -> bool:
        return True
        
    def strategy_name(self) -> str:
        return "mock_strategy"


def test_strategy_instantiation():
    """Test that a concrete implementation of the interface can be instantiated."""
    strategy = MockStrategy()
    assert strategy.strategy_name() == "mock_strategy"
    assert strategy.supports_weighting() is True
    
    merged = strategy.merge([{}, {}])
    assert merged["merged"] is True


def test_abstract_class_cannot_be_instantiated():
    """Test that the abstract base class cannot be instantiated directly."""
    with pytest.raises(TypeError):
        AdapterMergeStrategy()

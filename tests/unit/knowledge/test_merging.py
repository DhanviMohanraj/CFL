"""Tests for Merging.

Author: DriftAdapt Contributors
"""

from app.knowledge.merging.consolidation_strategy import SimpleConsolidation


def test_simple_consolidation():
    strategy = SimpleConsolidation()
    data = {"a": 1}
    result = strategy.consolidate(data, {})
    assert result == data

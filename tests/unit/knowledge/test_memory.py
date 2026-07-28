"""Tests for Prototype Memory.

Author: DriftAdapt Contributors
"""

from app.knowledge.memory.prototype_bank import PrototypeBank
from app.knowledge.memory.prototype_registry import PrototypeRegistry


def test_prototype_bank():
    bank = PrototypeBank(capacity=2)
    bank.add("k1", "v1")
    bank.add("k2", "v2")
    assert bank.get("k1") == "v1"
    
    bank.add("k3", "v3")  # Evicts k1
    assert bank.get("k1") is None
    assert bank.get("k3") == "v3"


def test_prototype_registry():
    registry = PrototypeRegistry()
    registry.register("p1", {"type": "clinic", "id": 1})
    
    metadata = registry.lookup("p1")
    assert metadata["type"] == "clinic"
    assert registry.lookup("p2") == {}

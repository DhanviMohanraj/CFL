"""Tests for Client Registry.

Author: DriftAdapt Contributors
"""

import pytest

from app.federated.client.client_registry import ClientRegistry
from app.federated.client.client_schema import ClientIdentity
from app.federated.client.client_exceptions import ClientRegistrationError


def test_registry_lifecycle():
    registry = ClientRegistry()
    identity = ClientIdentity(client_id="clinic_1")
    
    registry.register(identity)
    
    lookup = registry.lookup("clinic_1")
    assert lookup is not None
    assert lookup.client_id == "clinic_1"
    
    stats = registry.statistics()
    assert stats["total_registered"] == 1
    
    registry.unregister("clinic_1")
    assert registry.lookup("clinic_1") is None
    
    stats = registry.statistics()
    assert stats["total_registered"] == 0

def test_heartbeat_unknown_client():
    registry = ClientRegistry()
    with pytest.raises(ClientRegistrationError):
        registry.heartbeat("unknown_clinic")

"""Tests for Communication Registry.

Author: DriftAdapt Contributors
"""

import pytest

from app.federated.communication.communication_registry import CommunicationRegistry
from app.federated.communication.communication_session import CommunicationSession

def test_registry_lifecycle():
    registry = CommunicationRegistry()
    session = CommunicationSession("c1", "c2")
    
    registry.register_session(session)
    assert registry.lookup_session(session.session_id) is not None
    
    stats = registry.get_statistics()
    assert stats["active_sessions"] == 1
    
    session.set_completed()
    registry.remove_session(session.session_id)
    
    assert registry.lookup_session(session.session_id) is None
    
    stats = registry.get_statistics()
    assert stats["active_sessions"] == 0
    assert stats["completed_sessions"] == 1

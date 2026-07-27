"""Tests for Communication Session.

Author: DriftAdapt Contributors
"""

import pytest

from app.federated.communication.communication_session import CommunicationSession
from app.federated.communication.communication_exceptions import ProtocolError

def test_session_state_transitions():
    session = CommunicationSession("c1", "c2")
    assert session.state == "CREATED"
    
    session.set_preparing()
    assert session.state == "PREPARING"
    
    session.set_uploading()
    assert session.state == "UPLOADING"
    
    session.set_completed()
    assert session.state == "COMPLETED"

def test_invalid_state_transition():
    session = CommunicationSession("c1", "c2")
    
    with pytest.raises(ProtocolError):
        session._update_state("INVALID_STATE")

def test_add_bytes():
    session = CommunicationSession("c1", "c2")
    assert session.transferred_bytes == 0
    
    session.add_bytes(100)
    assert session.transferred_bytes == 100

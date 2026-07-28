"""Tests for Communication Manager.

Author: DriftAdapt Contributors
"""

import pytest
from typing import Optional

from app.federated.communication.communication_manager import CommunicationManager
from app.federated.communication.transport_protocol import TransportProtocol
from app.federated.communication.communication_schema import CommunicationMessage
from app.federated.communication.communication_exceptions import CommunicationError

class MockTransport(TransportProtocol):
    def connect(self) -> None:
        pass
    def disconnect(self) -> None:
        pass
    def send(self, message: CommunicationMessage) -> None:
        pass
    def receive(self, timeout: float = 60.0) -> Optional[CommunicationMessage]:
        return CommunicationMessage(
            message_id="m1",
            sender="c1",
            receiver="coordinator",
            message_type="UPLOAD",
            payload=b"fake_weights"
        )

def test_upload_success():
    transport = MockTransport()
    manager = CommunicationManager(transport)
    
    session_id = manager.upload("c1", b"fake_weights", {"version": "v1"})
    assert session_id is not None
    
    # Session is moved to completed, removed from active
    assert manager.status(session_id) is None

def test_download_success():
    transport = MockTransport()
    manager = CommunicationManager(transport)
    
    session = manager.download("c1")
    assert session.transferred_bytes > 0
    assert session.state == "COMPLETED"

def test_synchronize_success():
    transport = MockTransport()
    manager = CommunicationManager(transport)
    
    session_id = manager.synchronize(["c1", "c2"])
    assert session_id is not None

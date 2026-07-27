"""Tests for Transport Protocol.

Author: DriftAdapt Contributors
"""

import pytest

from app.federated.communication.transport_protocol import TransportProtocol
from app.federated.communication.communication_schema import CommunicationMessage

class MockProtocol(TransportProtocol):
    def connect(self) -> None:
        pass
    def disconnect(self) -> None:
        pass
    def send(self, message: CommunicationMessage) -> None:
        pass
    def receive(self, timeout: float = 60.0) -> None:
        pass

def test_protocol_instantiation():
    protocol = MockProtocol()
    
    # Abstract methods must be implemented
    assert hasattr(protocol, "connect")
    assert hasattr(protocol, "disconnect")
    assert hasattr(protocol, "send")
    assert hasattr(protocol, "receive")

def test_abstract_base_class():
    with pytest.raises(TypeError):
        TransportProtocol()

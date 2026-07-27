"""Tests for Communication Security.

Author: DriftAdapt Contributors
"""

import hashlib
import pytest

from app.federated.communication.communication_security import CommunicationSecurity
from app.federated.communication.communication_exceptions import PackageValidationError
from app.federated.communication.communication_schema import CommunicationMessage

def test_verify_checksum_valid():
    security = CommunicationSecurity()
    payload = b"hello_world"
    expected = hashlib.sha256(payload).hexdigest()
    
    assert security.verify_checksum(payload, expected) is True

def test_verify_checksum_invalid():
    security = CommunicationSecurity()
    payload = b"hello_world"
    expected = "invalid_hash"
    
    with pytest.raises(PackageValidationError):
        security.verify_checksum(payload, expected)

def test_verify_protocol_version():
    security = CommunicationSecurity()
    
    msg = CommunicationMessage(
        message_id="m1",
        sender="c1",
        receiver="c2",
        message_type="UPLOAD",
        metadata={"protocol_version": "1.0"}
    )
    
    assert security.verify_protocol_version(msg, "1.0") is True
    
    with pytest.raises(PackageValidationError):
        security.verify_protocol_version(msg, "2.0")

def test_authenticate_message():
    security = CommunicationSecurity()
    
    msg = CommunicationMessage(
        message_id="m1",
        sender="c1",
        receiver="c2",
        message_type="UPLOAD",
        metadata={"protocol_version": "1.0"}
    )
    
    assert security.authenticate_message(msg) is True

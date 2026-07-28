"""Tests for Message Validator.

Author: DriftAdapt Contributors
"""

import pytest

from app.federated.communication.message_validator import MessageValidator
from app.federated.communication.communication_schema import CommunicationMessage
from app.federated.communication.communication_exceptions import PackageValidationError

def test_validate_valid_message():
    validator = MessageValidator()
    
    msg = CommunicationMessage(
        message_id="m1",
        sender="c1",
        receiver="coordinator",
        message_type="REGISTER"
    )
    
    # Should not raise
    validator.validate_message(msg)

def test_validate_missing_fields():
    validator = MessageValidator()
    
    with pytest.raises(ValueError):
        # Pydantic will catch missing required fields before validator
        CommunicationMessage(
            sender="c1",
            receiver="coordinator",
            message_type="REGISTER"
        )

def test_validate_duplicate_message():
    validator = MessageValidator()
    
    msg1 = CommunicationMessage(
        message_id="m1",
        sender="c1",
        receiver="coordinator",
        message_type="REGISTER"
    )
    
    validator.validate_message(msg1)
    
    with pytest.raises(PackageValidationError):
        validator.validate_message(msg1)

def test_validate_payload():
    validator = MessageValidator()
    
    msg = CommunicationMessage(
        message_id="m1",
        sender="c1",
        receiver="coordinator",
        message_type="UPLOAD",
        payload=None
    )
    
    with pytest.raises(PackageValidationError):
        validator.validate_payload(msg)

"""DriftAdapt Message Validator.

Author: DriftAdapt Contributors
Purpose: Validates metadata and structural integrity of incoming/outgoing messages.
"""

import time
from typing import Set

from app.core.logging.logger_factory import LoggerFactory
from app.federated.communication.communication_exceptions import PackageValidationError
from app.federated.communication.communication_schema import CommunicationMessage


class MessageValidator:
    """Validates structural correctness of messages."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("MessageValidator")
        self._seen_messages: Set[str] = set()
        
    def validate_message(self, message: CommunicationMessage) -> None:
        """Validates all basic properties of a message."""
        if not message.message_id:
            raise PackageValidationError("Missing message_id.")
            
        if not message.message_type:
            raise PackageValidationError("Missing message_type.")
            
        if not message.sender or not message.receiver:
            raise PackageValidationError("Missing sender or receiver.")
            
        if message.timestamp <= 0 or message.timestamp > time.time() + 86400:  # Allow slight future drift
            raise PackageValidationError("Invalid message timestamp.")
            
        if message.message_id in self._seen_messages:
            raise PackageValidationError(f"Duplicate message detected: {message.message_id}")
            
        self._seen_messages.add(message.message_id)
        
    def validate_payload(self, message: CommunicationMessage) -> None:
        """Validates payload constraints."""
        if message.message_type in ["UPLOAD", "DOWNLOAD"] and not message.payload:
            raise PackageValidationError(f"Message type {message.message_type} requires a payload.")

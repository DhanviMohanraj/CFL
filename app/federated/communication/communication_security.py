"""DriftAdapt Communication Security Layer.

Author: DriftAdapt Contributors
Purpose: Validates package integrity, checksums, and authenticity.
"""

import hashlib

from app.core.logging.logger_factory import LoggerFactory
from app.federated.communication.communication_exceptions import PackageValidationError
from app.federated.communication.communication_schema import CommunicationMessage


class CommunicationSecurity:
    """Security verification layer for communication."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("CommunicationSecurity")
        
    def verify_checksum(self, payload: bytes, expected_checksum: str) -> bool:
        """Verifies payload integrity."""
        if expected_checksum and not payload:
            raise PackageValidationError("Expected checksum but payload is empty.")
            
        if payload and expected_checksum:
            actual_checksum = hashlib.sha256(payload).hexdigest()
            if actual_checksum != expected_checksum:
                raise PackageValidationError("Payload checksum mismatch.")
        return True
        
    def verify_protocol_version(self, message: CommunicationMessage, expected_version: str = "1.0") -> bool:
        """Verifies that the message protocol matches the system protocol."""
        version = message.metadata.get("protocol_version", "unknown")
        if version != expected_version:
            raise PackageValidationError(f"Protocol version mismatch. Expected {expected_version}, got {version}")
        return True
        
    def verify_clinic_identity(self, clinic_id: str) -> bool:
        """Simulates authenticating a clinic ID."""
        if not clinic_id:
            raise PackageValidationError("Clinic ID is missing or invalid.")
        return True
        
    def authenticate_message(self, message: CommunicationMessage) -> bool:
        """Verifies all aspects of message authenticity."""
        try:
            self.verify_clinic_identity(message.sender)
            self.verify_protocol_version(message)
            return True
        except Exception as e:
            self._logger.warning(f"Message authentication failed: {e}")
            raise PackageValidationError(f"Message authentication failed: {e}")

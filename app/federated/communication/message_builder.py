"""DriftAdapt Message Builder.

Author: DriftAdapt Contributors
Purpose: Constructs standard communication envelopes.
"""

import uuid
from typing import Any, Dict, Optional

from app.federated.communication.communication_schema import CommunicationMessage


class MessageBuilder:
    """Builder for CommunicationMessage envelopes."""
    
    def __init__(self, sender_id: str, protocol_version: str = "1.0") -> None:
        self._sender = sender_id
        self._protocol_version = protocol_version
        
    def _build(self, receiver: str, msg_type: str, payload: Optional[bytes] = None, metadata: Optional[Dict[str, Any]] = None, priority: int = 0) -> CommunicationMessage:
        meta = metadata or {}
        meta["protocol_version"] = self._protocol_version
        
        return CommunicationMessage(
            message_id=str(uuid.uuid4()),
            sender=self._sender,
            receiver=receiver,
            message_type=msg_type,
            payload=payload,
            metadata=meta,
            priority=priority
        )
        
    def build_register(self, receiver: str, metadata: Optional[Dict[str, Any]] = None) -> CommunicationMessage:
        return self._build(receiver, "REGISTER", metadata=metadata)
        
    def build_upload(self, receiver: str, payload: bytes, metadata: Optional[Dict[str, Any]] = None) -> CommunicationMessage:
        return self._build(receiver, "UPLOAD", payload=payload, metadata=metadata)
        
    def build_download(self, receiver: str, metadata: Optional[Dict[str, Any]] = None) -> CommunicationMessage:
        return self._build(receiver, "DOWNLOAD", metadata=metadata)
        
    def build_sync_request(self, receiver: str, metadata: Optional[Dict[str, Any]] = None) -> CommunicationMessage:
        return self._build(receiver, "SYNC_REQUEST", metadata=metadata)
        
    def build_sync_response(self, receiver: str, payload: Optional[bytes] = None, metadata: Optional[Dict[str, Any]] = None) -> CommunicationMessage:
        return self._build(receiver, "SYNC_RESPONSE", payload=payload, metadata=metadata)
        
    def build_heartbeat(self, receiver: str) -> CommunicationMessage:
        return self._build(receiver, "HEARTBEAT")
        
    def build_status(self, receiver: str, metadata: Optional[Dict[str, Any]] = None) -> CommunicationMessage:
        return self._build(receiver, "STATUS", metadata=metadata)
        
    def build_error(self, receiver: str, error_details: Dict[str, Any]) -> CommunicationMessage:
        return self._build(receiver, "ERROR", metadata=error_details, priority=99)
        
    def build_acknowledgement(self, receiver: str, target_message_id: str) -> CommunicationMessage:
        return self._build(receiver, "ACKNOWLEDGEMENT", metadata={"ack_for": target_message_id})

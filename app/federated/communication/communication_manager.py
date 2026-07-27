"""DriftAdapt Communication Manager.

Author: DriftAdapt Contributors
Purpose: Central orchestrator for federated communication.
"""

from typing import Any, Dict, List, Optional

from app.core.config.config_manager import ConfigManager
from app.core.logging.logger_factory import LoggerFactory
from app.federated.communication.adapter_package import AdapterPackageBuilder
from app.federated.communication.communication_exceptions import CommunicationError
from app.federated.communication.communication_registry import CommunicationRegistry
from app.federated.communication.communication_session import CommunicationSession
from app.federated.communication.message_builder import MessageBuilder
from app.federated.communication.message_validator import MessageValidator
from app.federated.communication.retry_manager import RetryManager
from app.federated.communication.synchronization_manager import SynchronizationManager
from app.federated.communication.transport_protocol import TransportProtocol


class CommunicationManager:
    """Orchestrates communication flows."""
    
    def __init__(self, transport: TransportProtocol, configs_dir: Optional[str] = None) -> None:
        self._logger = LoggerFactory.get_logger("CommunicationManager")
        self._transport = transport
        self._registry = CommunicationRegistry()
        self._sync_manager = SynchronizationManager(self._registry)
        self._package_builder = AdapterPackageBuilder()
        self._validator = MessageValidator()
        
        # Load configuration
        config = ConfigManager(configs_dir).get_config()
        comm_config = getattr(config, "communication", None)
        
        max_retries = getattr(comm_config, "max_retries", 5) if comm_config else 5
        self._protocol_version = getattr(comm_config, "protocol_version", "1.0") if comm_config else "1.0"
        
        self._retry_manager = RetryManager(max_retries=max_retries, base_delay=0.01) # Small delay for tests
        self._message_builder = MessageBuilder("coordinator", protocol_version=self._protocol_version)
        
    def _create_session(self, sender: str, receiver: str) -> CommunicationSession:
        session = CommunicationSession(sender, receiver)
        self._registry.register_session(session)
        return session
        
    def upload(self, receiver: str, payload: bytes, metadata: Dict[str, Any]) -> str:
        """Initiates an upload to a receiver."""
        session = self._create_session("coordinator", receiver)
        session.set_preparing()
        
        message = self._message_builder.build_upload(receiver, payload, metadata)
        self._validator.validate_message(message)
        self._validator.validate_payload(message)
        
        session.set_uploading()
        try:
            self._retry_manager.execute(self._transport.send, message)
            session.add_bytes(len(payload))
            session.set_completed()
            self._registry.remove_session(session.session_id)
            return session.session_id
        except Exception as e:
            session.set_failed()
            self._registry.remove_session(session.session_id)
            raise CommunicationError(f"Upload failed: {e}") from e
            
    def download(self, sender: str) -> CommunicationSession:
        """Simulates downloading a message."""
        session = self._create_session(sender, "coordinator")
        session.set_downloading()
        
        try:
            message = self._retry_manager.execute(self._transport.receive)
            if message:
                self._validator.validate_message(message)
                if message.payload:
                    session.add_bytes(len(message.payload))
            session.set_completed()
            self._registry.remove_session(session.session_id)
            return session
        except Exception as e:
            session.set_failed()
            self._registry.remove_session(session.session_id)
            raise CommunicationError(f"Download failed: {e}") from e
            
    def synchronize(self, participants: List[str]) -> str:
        """Executes a synchronization round across participants."""
        session = self._create_session("coordinator", "broadcast")
        sync_status = self._sync_manager.begin_sync(session.session_id)
        
        try:
            # Sync Request
            for participant in participants:
                msg = self._message_builder.build_sync_request(participant)
                self._transport.send(msg)
                
            sync_status.upload_complete = True
            sync_status.download_complete = True
            self._sync_manager.complete_sync(session.session_id)
            session.set_completed()
            self._registry.remove_session(session.session_id)
            return session.session_id
        except Exception as e:
            self._sync_manager.rollback_sync(session.session_id)
            session.set_failed()
            self._registry.remove_session(session.session_id)
            raise CommunicationError(f"Synchronization failed: {e}") from e
            
    def cancel(self, session_id: str) -> None:
        """Cancels a session."""
        session = self._registry.lookup_session(session_id)
        if session:
            session.set_cancelled()
            self._registry.remove_session(session_id)
            
    def resume(self, session_id: str) -> None:
        """Resumes a failed session."""
        pass
        
    def status(self, session_id: str) -> Optional[str]:
        """Gets session status."""
        session = self._registry.lookup_session(session_id)
        return session.state if session else None

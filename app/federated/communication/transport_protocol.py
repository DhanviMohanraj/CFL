"""DriftAdapt Transport Protocol Interface.

Author: DriftAdapt Contributors
Purpose: Abstract definition for network transport layers.
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.federated.communication.communication_schema import CommunicationMessage


class TransportProtocol(ABC):
    """Abstract interface for transmitting messages over a network."""
    
    @abstractmethod
    def connect(self) -> None:
        """Establishes connection."""
        pass
        
    @abstractmethod
    def disconnect(self) -> None:
        """Terminates connection."""
        pass
        
    @abstractmethod
    def send(self, message: CommunicationMessage) -> None:
        """Sends a message."""
        pass
        
    @abstractmethod
    def receive(self, timeout: float = 60.0) -> Optional[CommunicationMessage]:
        """Receives a message."""
        pass

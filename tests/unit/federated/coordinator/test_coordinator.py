"""Tests for Federated Coordinator.

Author: DriftAdapt Contributors
"""

import pytest
import threading
import time

from app.federated.coordinator.coordinator import FederatedCoordinator
from app.federated.coordinator.coordinator_exceptions import CoordinatorFailure
from app.federated.communication.communication_manager import CommunicationManager
from app.federated.communication.transport_protocol import TransportProtocol
from app.federated.communication.communication_schema import CommunicationMessage
from typing import Optional

class MockTransport(TransportProtocol):
    def connect(self) -> None: pass
    def disconnect(self) -> None: pass
    def send(self, message: CommunicationMessage) -> None: pass
    def receive(self, timeout: float = 60.0) -> Optional[CommunicationMessage]: return None

def test_coordinator_lifecycle():
    transport = MockTransport()
    comm_manager = CommunicationManager(transport)
    
    coordinator = FederatedCoordinator(comm_manager)
    coordinator.initialize()
    assert coordinator.status() == "IDLE"
    
    # We run start_round in a thread because it blocks on the barrier
    clients = ["c1", "c2"]
    
    def run_coordinator():
        try:
            coordinator.start_round(clients)
        except CoordinatorFailure:
            pass
            
    thread = threading.Thread(target=run_coordinator)
    thread.start()
    
    time.sleep(0.1)
    
    assert coordinator.status() == "INITIALIZED"
    
    coordinator.complete_round()
    thread.join()
    
    assert coordinator.status() == "IDLE"

def test_coordinator_cancel():
    transport = MockTransport()
    comm_manager = CommunicationManager(transport)
    
    coordinator = FederatedCoordinator(comm_manager)
    coordinator.initialize()
    
    def run_coordinator():
        try:
            coordinator.start_round(["c1"])
        except CoordinatorFailure:
            pass
            
    thread = threading.Thread(target=run_coordinator)
    thread.start()
    
    time.sleep(0.1)
    
    coordinator.cancel_round()
    thread.join()
    
    assert coordinator.status() == "IDLE"

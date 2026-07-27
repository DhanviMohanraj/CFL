"""Tests for Synchronization Manager.

Author: DriftAdapt Contributors
"""

import pytest

from app.federated.communication.synchronization_manager import SynchronizationManager
from app.federated.communication.communication_registry import CommunicationRegistry
from app.federated.communication.communication_exceptions import SynchronizationError

def test_begin_and_complete_sync():
    registry = CommunicationRegistry()
    sync_manager = SynchronizationManager(registry)
    
    session_id = "sync_123"
    status = sync_manager.begin_sync(session_id)
    assert status.session_id == session_id
    assert status.current_state == "INIT"
    
    sync_manager.complete_sync(session_id)
    
    history = sync_manager.history()
    assert len(history) == 1
    assert history[0].current_state == "COMPLETED"

def test_rollback_sync():
    registry = CommunicationRegistry()
    sync_manager = SynchronizationManager(registry)
    
    session_id = "sync_123"
    sync_manager.begin_sync(session_id)
    sync_manager.rollback_sync(session_id)
    
    history = sync_manager.history()
    assert len(history) == 1
    assert history[0].current_state == "ROLLED_BACK"

def test_complete_invalid_sync():
    registry = CommunicationRegistry()
    sync_manager = SynchronizationManager(registry)
    
    with pytest.raises(SynchronizationError):
        sync_manager.complete_sync("invalid")

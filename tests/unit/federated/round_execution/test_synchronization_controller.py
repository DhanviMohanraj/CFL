"""Tests for Synchronization Controller.

Author: DriftAdapt Contributors
"""

import time
import threading
from app.federated.round_execution.synchronization_controller import SynchronizationController


def test_synchronization_controller():
    controller = SynchronizationController(2)
    
    controller.client_ready("c1")
    assert controller.wait(timeout=0.1) is False
    
    controller.client_ready("c2")
    assert controller.wait(timeout=0.1) is True
    
    controller.reset()
    assert controller.wait(timeout=0.1) is False
    
    controller.abort()
    assert controller.wait(timeout=0.1) is True

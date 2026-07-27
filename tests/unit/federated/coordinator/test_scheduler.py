"""Tests for Scheduler.

Author: DriftAdapt Contributors
"""

import time
import pytest

from app.federated.coordinator.scheduler import Scheduler


def test_scheduler_execution():
    scheduler = Scheduler()
    
    executed = False
    def task():
        nonlocal executed
        executed = True
        
    scheduler.schedule_task(0.01, task)
    time.sleep(0.05)
    
    assert executed
    
def test_scheduler_cancel():
    scheduler = Scheduler()
    
    executed = False
    def task():
        nonlocal executed
        executed = True
        
    scheduler.schedule_task(0.05, task)
    scheduler.cancel_all()
    
    time.sleep(0.1)
    assert not executed

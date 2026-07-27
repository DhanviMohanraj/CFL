"""Tests for Retry Manager.

Author: DriftAdapt Contributors
"""

import pytest

from app.federated.communication.retry_manager import RetryManager
from app.federated.communication.communication_exceptions import RetryLimitExceeded

def test_successful_operation():
    manager = RetryManager(max_retries=3, base_delay=0.01)
    
    def operation():
        return "success"
        
    result = manager.execute(operation)
    assert result == "success"

def test_retry_eventual_success():
    manager = RetryManager(max_retries=3, base_delay=0.01)
    
    attempts = 0
    def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Failed")
        return "success"
        
    result = manager.execute(operation)
    assert result == "success"
    assert attempts == 3

def test_retry_exhaustion():
    manager = RetryManager(max_retries=2, base_delay=0.01)
    
    def operation():
        raise ValueError("Failed")
        
    with pytest.raises(RetryLimitExceeded):
        manager.execute(operation)

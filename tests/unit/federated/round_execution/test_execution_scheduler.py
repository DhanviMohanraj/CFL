"""Tests for Execution Scheduler.

Author: DriftAdapt Contributors
"""

import pytest
from app.federated.round_execution.execution_scheduler import ExecutionScheduler


def test_execution_scheduler():
    scheduler = ExecutionScheduler(retry_attempts=2)
    
    attempts = 0
    def mock_func():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ValueError("fail")
        return "success"
        
    res = scheduler.execute_with_retry(mock_func)
    assert res == "success"
    assert attempts == 2
    
    def failing_func():
        raise ValueError("fail forever")
        
    with pytest.raises(ValueError):
        scheduler.execute_with_retry(failing_func)

"""Tests for Resource Allocator.

Author: DriftAdapt Contributors
"""

import pytest
from app.training.resource_allocator import ResourceAllocator


def test_resource_allocator():
    allocator = ResourceAllocator(max_parallel_clients=2)
    
    assert allocator.can_allocate_client() is True
    
    allocator.allocate_client()
    allocator.allocate_client()
    
    assert allocator.can_allocate_client() is False
    
    with pytest.raises(RuntimeError):
        allocator.allocate_client()
        
    allocator.deallocate_client()
    assert allocator.can_allocate_client() is True
    
    usage = allocator.get_resource_usage()
    assert usage["active_clients"] == 1
    assert usage["memory_usage_mb"] == 250

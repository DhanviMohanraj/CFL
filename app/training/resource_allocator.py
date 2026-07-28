"""DriftAdapt Resource Allocator.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any


class ResourceAllocator:
    """Monitors and manages resources across the experiment."""
    
    def __init__(self, max_parallel_clients: int = 4) -> None:
        self.max_parallel_clients = max_parallel_clients
        self.active_clients = 0
        
    def can_allocate_client(self) -> bool:
        """Checks if another client can be allocated."""
        return self.active_clients < self.max_parallel_clients
        
    def allocate_client(self) -> None:
        if not self.can_allocate_client():
            raise RuntimeError("Maximum parallel clients reached.")
        self.active_clients += 1
        
    def deallocate_client(self) -> None:
        if self.active_clients > 0:
            self.active_clients -= 1
            
    def get_resource_usage(self) -> Dict[str, Any]:
        """Returns mock resource usage metrics."""
        return {
            "active_clients": self.active_clients,
            "max_clients": self.max_parallel_clients,
            "memory_usage_mb": self.active_clients * 250
        }

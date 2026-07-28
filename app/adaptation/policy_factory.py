"""DriftAdapt Policy Factory.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, Optional
from app.adaptation.policy_registry import PolicyRegistry
from app.adaptation.adaptation_exceptions import PolicyEvaluationError


class PolicyFactory:
    """Factory to retrieve and instantiate adaptation policies."""
    
    def __init__(self, registry: PolicyRegistry) -> None:
        self.registry = registry
        
    def get_policy(self, name: str) -> Any:
        policy = self.registry.lookup(name)
        if not policy:
            raise PolicyEvaluationError(f"Policy '{name}' not found in registry.")
        return policy
        
    def get_all_policies(self) -> Dict[str, Any]:
        return self.registry.all_policies()

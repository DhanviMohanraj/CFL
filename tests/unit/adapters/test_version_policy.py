"""Tests for Version Policy Manager.

Author: DriftAdapt Contributors
"""

import pytest

from app.adapters.exceptions import PolicyViolation
from app.adapters.version_policy import VersionPolicyManager


def test_policy_enforcement():
    """Test policy manager enforces clinic version limits."""
    policy = VersionPolicyManager()
    policy.max_versions_per_clinic = 5
    
    # Under limit should pass silently
    policy.enforce_clinic_limit(4)
    
    # At limit should fail
    with pytest.raises(PolicyViolation, match="limit of 5"):
        policy.enforce_clinic_limit(5)
        
    # Over limit should fail
    with pytest.raises(PolicyViolation, match="limit of 5"):
        policy.enforce_clinic_limit(6)

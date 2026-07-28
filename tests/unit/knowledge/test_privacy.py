"""Tests for Privacy.

Author: DriftAdapt Contributors
"""

import pytest
from app.knowledge.privacy.privacy_accountant import PrivacyAccountant
from app.knowledge.consolidation_exceptions import PrivacyBudgetExceededError


def test_privacy_accountant():
    accountant = PrivacyAccountant(epsilon_budget=8.0)
    
    accountant.consume(2.0)
    assert accountant.get_remaining() == 6.0
    
    with pytest.raises(PrivacyBudgetExceededError):
        accountant.consume(7.0)

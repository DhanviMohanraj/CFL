"""Tests for Client Dispatcher.

Author: DriftAdapt Contributors
"""

import pytest
from app.federated.round_execution.client_dispatcher import ClientDispatcher
from app.federated.round_execution.execution_exceptions import ClientDispatchError


def test_client_dispatcher():
    dispatcher = ClientDispatcher()
    
    dispatcher.dispatch(["c1"], 1, {})
    
    with pytest.raises(ClientDispatchError):
        dispatcher.dispatch([], 1, {})

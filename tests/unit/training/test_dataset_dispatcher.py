"""Tests for Dataset Dispatcher.

Author: DriftAdapt Contributors
"""

import pytest
from app.training.dataset_dispatcher import DatasetDispatcher
from app.training.experiment_exceptions import DatasetDispatchError


def test_dataset_dispatcher():
    dispatcher = DatasetDispatcher()
    
    path = dispatcher.dispatch("clinic_01", 1)
    assert path == "datasets/clinic_01/month_01.jsonl"
    
    path = dispatcher.dispatch("clinic_02", 12)
    assert path == "datasets/clinic_02/month_12.jsonl"
    
    with pytest.raises(DatasetDispatchError):
        dispatcher.dispatch("", 1)
        
    with pytest.raises(DatasetDispatchError):
        dispatcher.dispatch("clinic_01", 0)

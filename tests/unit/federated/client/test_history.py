"""Tests for Training History.

Author: DriftAdapt Contributors
"""

import json
import pytest

from app.federated.client.training_history import TrainingHistory


def test_history_tracking():
    history = TrainingHistory()
    
    history.add_epoch(1, 0.5, 0.8)
    history.add_epoch(2, 0.4, 0.85)
    
    records = history.get_history()
    assert len(records) == 2
    assert records[0].epoch == 1
    assert records[1].loss == 0.4
    
    json_export = history.export_json()
    assert isinstance(json_export, str)
    data = json.loads(json_export)
    assert len(data) == 2
    
    history.clear()
    assert len(history.get_history()) == 0

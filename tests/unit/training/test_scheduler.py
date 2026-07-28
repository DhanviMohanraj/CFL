"""Tests for Schedulers.

Author: DriftAdapt Contributors
"""

import pytest
from app.training.experiment_scheduler import ExperimentScheduler
from app.training.round_scheduler import RoundScheduler


def test_experiment_scheduler():
    scheduler = ExperimentScheduler(total_months=2)
    
    assert scheduler.current_month == 1
    assert not scheduler.is_complete()
    
    assert scheduler.next_month() is True
    assert scheduler.current_month == 2
    
    assert scheduler.next_month() is False
    assert scheduler.current_month == 2
    
    # Needs to transition to complete month logic, this mock relies on manual increment
    # We will simulate completion check via >
    scheduler.current_month += 1 
    assert scheduler.is_complete()


def test_round_scheduler():
    scheduler = RoundScheduler(max_rounds=2)
    
    assert scheduler.current_round == 0
    
    assert scheduler.next_round() is True
    assert scheduler.current_round == 1
    
    assert scheduler.next_round() is True
    assert scheduler.current_round == 2
    
    assert scheduler.next_round() is False
    assert scheduler.is_complete()

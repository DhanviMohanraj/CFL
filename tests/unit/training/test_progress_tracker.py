"""Tests for Progress Tracker.

Author: DriftAdapt Contributors
"""

from app.training.progress_tracker import ProgressTracker


def test_progress_tracker():
    tracker = ProgressTracker(total_rounds=10, total_months=2)
    
    assert tracker.get_completion_percentage() == 0.0
    
    tracker.record_round_completion()
    tracker.record_round_completion()
    
    assert tracker.get_completion_percentage() == 20.0
    
    tracker.record_month_completion()
    assert tracker.completed_months == 1
    
    assert tracker.get_elapsed_time() >= 0.0

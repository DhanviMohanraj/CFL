"""DriftAdapt Progress Tracker.

Author: DriftAdapt Contributors
"""

import time


class ProgressTracker:
    """Tracks completion percentage and elapsed time for an experiment."""
    
    def __init__(self, total_rounds: int, total_months: int) -> None:
        self.total_rounds = total_rounds
        self.total_months = total_months
        
        self.completed_rounds = 0
        self.completed_months = 0
        self.start_time = time.time()
        
    def record_round_completion(self) -> None:
        self.completed_rounds += 1
        
    def record_month_completion(self) -> None:
        self.completed_months += 1
        
    def get_completion_percentage(self) -> float:
        if self.total_rounds == 0:
            return 0.0
        return (self.completed_rounds / self.total_rounds) * 100.0
        
    def get_elapsed_time(self) -> float:
        return time.time() - self.start_time

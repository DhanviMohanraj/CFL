"""DriftAdapt Experiment Scheduler.

Author: DriftAdapt Contributors
"""

class ExperimentScheduler:
    """Schedules progression of an experiment across months."""
    
    def __init__(self, total_months: int) -> None:
        self.total_months = total_months
        self.current_month = 1
        
    def next_month(self) -> bool:
        if self.current_month < self.total_months:
            self.current_month += 1
            return True
        return False
        
    def is_complete(self) -> bool:
        return self.current_month > self.total_months
        
    def remaining_months(self) -> int:
        return max(0, self.total_months - self.current_month + 1)

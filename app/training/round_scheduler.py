"""DriftAdapt Round Scheduler.

Author: DriftAdapt Contributors
"""


class RoundScheduler:
    """Manages tracking of federated communication rounds."""
    
    def __init__(self, max_rounds: int) -> None:
        self.max_rounds = max_rounds
        self.current_round = 0
        
    def next_round(self) -> bool:
        """Advances to the next round if possible. Returns True if advanced."""
        if self.current_round < self.max_rounds:
            self.current_round += 1
            return True
        return False
        
    def is_complete(self) -> bool:
        """Returns True if all rounds are completed."""
        return self.current_round >= self.max_rounds
        
    def get_round_info(self) -> dict:
        return {
            "current_round": self.current_round,
            "max_rounds": self.max_rounds,
            "is_complete": self.is_complete()
        }

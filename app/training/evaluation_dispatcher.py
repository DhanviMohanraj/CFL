"""DriftAdapt Evaluation Dispatcher.

Author: DriftAdapt Contributors
"""

from app.training.experiment_exceptions import EvaluationDispatchError


class EvaluationDispatcher:
    """Dispatches evaluation tasks."""
    
    def __init__(self) -> None:
        pass
        
    def dispatch_monthly_evaluation(self, month: int) -> None:
        """Triggers monthly evaluation."""
        if month <= 0:
            raise EvaluationDispatchError("month must be > 0.")
        # Mocks monthly evaluation dispatch logic
        pass
        
    def dispatch_final_evaluation(self) -> None:
        """Triggers the final comprehensive evaluation."""
        # Mocks final evaluation dispatch logic
        pass

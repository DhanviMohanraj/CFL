"""DriftAdapt Validation Manager.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, Tuple


class ValidationManager:
    """Handles validation metrics and early stopping."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.early_stopping = config.get("early_stopping", True)
        self.patience = config.get("patience", 3)
        
        self.best_loss = float("inf")
        self.epochs_without_improvement = 0
        
    def evaluate(self, predictions, targets) -> Dict[str, float]:
        """Computes evaluation metrics (mocked)."""
        acc = float((predictions == targets).float().mean().item()) if len(targets) > 0 else 0.0
        return {
            "accuracy": acc,
            "precision": acc,
            "recall": acc,
            "f1": acc
        }
        
    def check_early_stopping(self, val_loss: float) -> Tuple[bool, bool]:
        """
        Checks if early stopping should be triggered and if the model is the best so far.
        Returns (stop_training, is_best).
        """
        is_best = False
        if val_loss < self.best_loss:
            self.best_loss = val_loss
            self.epochs_without_improvement = 0
            is_best = True
        else:
            self.epochs_without_improvement += 1
            
        stop_training = self.early_stopping and self.epochs_without_improvement >= self.patience
        return stop_training, is_best

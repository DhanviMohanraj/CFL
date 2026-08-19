import flwr as fl
from typing import Dict, List, Tuple
from collections import OrderedDict
import torch
import numpy as np
from app.training.local_trainer import LocalLoRATrainer

class FlowerClient(fl.client.NumPyClient):
    def __init__(self, trainer: LocalLoRATrainer):
        self.trainer = trainer
        self.trainer.initialize()
        self.trainer.prepare()

    def get_parameters(self, config: Dict[str, fl.common.Scalar]) -> List[np.ndarray]:
        """Extract PEFT model parameters as a list of NumPy arrays."""
        # Only extract trainable parameters (LoRA weights)
        peft_state_dict = {
            k: v.cpu().numpy() 
            for k, v in self.trainer.model.state_dict().items() 
            if v.requires_grad or "lora" in k.lower()
        }
        return list(peft_state_dict.values())

    def set_parameters(self, parameters: List[np.ndarray]):
        """Inject aggregated parameters back into the PEFT model."""
        keys = [k for k, v in self.trainer.model.state_dict().items() if v.requires_grad or "lora" in k.lower()]
        
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in zip(keys, parameters)})
        self.trainer.model.load_state_dict(state_dict, strict=False)

    def fit(
        self, parameters: List[np.ndarray], config: Dict[str, fl.common.Scalar]
    ) -> Tuple[List[np.ndarray], int, Dict]:
        """Train the model locally."""
        if parameters:
            self.set_parameters(parameters)
        
        self.trainer.train()
        
        # Get history from HuggingFace Trainer
        history = self.trainer.trainer.state.log_history
        final_loss = history[-1].get("loss", 0.0) if history else 0.0

        return self.get_parameters(config={}), len(self.trainer.train_dataset), {"loss": final_loss}

    def evaluate(
        self, parameters: List[np.ndarray], config: Dict[str, fl.common.Scalar]
    ) -> Tuple[float, int, Dict]:
        """Evaluate the model locally."""
        self.set_parameters(parameters)
        
        metrics = self.trainer.trainer.evaluate()
        loss = metrics.get("eval_loss", 0.0)
        
        return float(loss), len(self.trainer.val_dataset), {"eval_loss": float(loss)}

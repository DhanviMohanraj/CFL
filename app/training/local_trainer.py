"""DriftAdapt Local LoRA Trainer.

Author: DriftAdapt Contributors
"""

import os
from typing import Dict, Any, Optional

from app.core.metrics.metrics_bus import MetricsBus
from app.training.training_state import TrainingState
from app.training.trainer_logger import TrainerLogger
from app.training.trainer_metrics import TrainerMetrics
from app.training.personalization_engine import PersonalizationEngine
from app.training.trainer_exceptions import TrainingExecutionError
from app.training.dataset_loader import DatasetLoader
from app.training.dataset_tokenizer import DatasetTokenizer

from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling

class LocalLoRATrainer:
    """Executes local LoRA fine-tuning for a specific clinic."""
    
    def __init__(
        self,
        trainer_id: str,
        clinic_id: str,
        month: int,
        config: Dict[str, Any],
        metrics_bus: MetricsBus
    ) -> None:
        self.trainer_id = trainer_id
        self.clinic_id = clinic_id
        self.month = month
        self.config = config
        
        self.state = TrainingState.CREATED
        self.logger = TrainerLogger(trainer_id)
        self.metrics = TrainerMetrics(metrics_bus)
        
        self.personalization_engine = PersonalizationEngine(config)
        self.dataset_loader = DatasetLoader(config)
        
        self.model = None
        self.tokenizer = None
        self.train_dataset = None
        self.val_dataset = None
        
    def initialize(self) -> None:
        """Initializes the model and components for training."""
        self.state = TrainingState.INITIALIZING
        
        try:
            self.model, self.tokenizer = self.personalization_engine.prepare_model()
            self.metrics.publish_event("training.started", tags={"clinic": self.clinic_id, "month": self.month})
            self.logger.info(f"Trainer initialized for {self.clinic_id}, month {self.month}.")
        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            self.state = TrainingState.CANCELLED
            raise TrainingExecutionError(f"Initialization failed: {e}")
        
    def prepare(self) -> None:
        """Prepares datasets."""
        self.state = TrainingState.PREPARING_DATA
        self.logger.info("Preparing data...")
        
        try:
            dataset = self.dataset_loader.load(self.clinic_id, self.month)
            
            # Split into train and val
            split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
            
            dataset_tokenizer = DatasetTokenizer(self.tokenizer, self.config)
            self.train_dataset = dataset_tokenizer.tokenize(split_dataset['train'])
            self.val_dataset = dataset_tokenizer.tokenize(split_dataset['test'])
            
            self.logger.info("Data preparation completed.")
        except Exception as e:
            self.logger.error(f"Data preparation failed: {str(e)}")
            self.state = TrainingState.CANCELLED
            raise TrainingExecutionError(f"Data preparation failed: {e}")
        
    def train(self) -> None:
        """Executes the training loop."""
        self.state = TrainingState.TRAINING
        
        try:
            output_dir = self.config.get("output_dir", "./results")
            
            training_args = TrainingArguments(
                output_dir=output_dir,
                per_device_train_batch_size=self.config.get("batch_size", 4),
                gradient_accumulation_steps=self.config.get("gradient_accumulation_steps", 4),
                warmup_steps=self.config.get("warmup_steps", 10),
                num_train_epochs=self.config.get("epochs", 3),
                learning_rate=self.config.get("learning_rate", 2e-4),
                fp16=self.config.get("fp16", True),
                bf16=self.config.get("bf16", False),
                logging_steps=10,
                eval_strategy="epoch",
                save_strategy="epoch",
                load_best_model_at_end=True
            )
            
            data_collator = DataCollatorForLanguageModeling(tokenizer=self.tokenizer, mlm=False)
            
            self.trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=self.train_dataset,
                eval_dataset=self.val_dataset,
                data_collator=data_collator
            )
            
            self.logger.info("Starting training...")
            train_result = self.trainer.train()
            
            self.metrics.publish_value("training.loss", train_result.training_loss, tags={"clinic": self.clinic_id})
            
            self.state = TrainingState.COMPLETED
            self.metrics.publish_event("training.completed")
            self.logger.info("Training completed.")
            
        except Exception as e:
            self.logger.error(f"Training failed: {str(e)}")
            self.state = TrainingState.CANCELLED
            raise TrainingExecutionError(f"Training failed: {e}")
        
    def export_adapter(self) -> str:
        self.state = TrainingState.EXPORTING
        
        export_path = os.path.join(self.config.get("output_dir", "./results"), "final_adapter")
        self.model.save_pretrained(export_path)
        
        self.metrics.publish_event("adapter.exported", tags={"clinic": self.clinic_id})
        self.logger.info(f"Adapter exported to {export_path}")
        return export_path
        
    def cleanup(self) -> None:
        self.model = None
        self.tokenizer = None
        self.trainer = None
        self.train_dataset = None
        self.val_dataset = None
        self.logger.info("Trainer resources cleaned up.")
        
    def status(self) -> str:
        return self.state.value

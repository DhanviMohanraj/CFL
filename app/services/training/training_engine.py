"""DriftAdapt Training Engine.

Author: DriftAdapt Contributors
Purpose: Exposes the core PyTorch loop for fine-tuning LoRA adapters.
"""

import time
import torch
from typing import Optional, Any
from torch.utils.data import DataLoader
from peft import PeftModel

from app.core.logging import LoggerFactory
from app.schemas.training_config import TrainingConfiguration
from app.schemas.training_metrics import TrainingMetrics
from app.schemas.training_checkpoint import TrainingCheckpoint

from app.services.training.optimizer_service import OptimizerService
from app.services.training.scheduler_service import SchedulerService
from app.services.training.gradient_manager import GradientManager
from app.services.training.early_stopping import EarlyStoppingService
from app.services.training.checkpoint_service import CheckpointService
from app.services.training.resource_monitor import ResourceMonitor
from app.services.training.training_monitor import TrainingMonitor
from app.services.training.metrics_service import MetricsService


class TrainingEngine:
    """Core engine executing the local PyTorch personalization loop."""

    def __init__(
        self,
        optimizer_service: OptimizerService,
        scheduler_service: SchedulerService,
        gradient_manager: GradientManager,
        early_stopping: EarlyStoppingService,
        checkpoint_service: CheckpointService,
        resource_monitor: ResourceMonitor,
        training_monitor: TrainingMonitor,
        metrics_service: MetricsService
    ) -> None:
        self._logger = LoggerFactory.get_logger("TrainingEngine")

        self._opt_service = optimizer_service
        self._sched_service = scheduler_service
        self._grad_manager = gradient_manager
        self._early_stopping = early_stopping
        self._checkpoint_service = checkpoint_service
        self._resource_monitor = resource_monitor
        self._training_monitor = training_monitor
        self._metrics_service = metrics_service

        self._stop_requested = False

    def request_stop(self) -> None:
        """Interrupts the active training loop gracefully."""
        self._stop_requested = True
        self._logger.info("Graceful stop requested. Training will halt after the current step.")

    def run(
        self,
        model: PeftModel,
        train_dataloader: DataLoader[Any],
        val_dataloader: Optional[DataLoader[Any]],
        config: TrainingConfiguration,
        adapter_id: str,
        continual_learning_round: int,
        resume_checkpoint: Optional[str] = None
    ) -> Optional[TrainingCheckpoint]:
        """Executes the fine-tuning loop.

        Args:
            model: The initialized PEFT model (frozen base, trainable adapter).
            train_dataloader: DataLoader for training data.
            val_dataloader: DataLoader for validation data (optional).
            config: Training hyperparameters.
            adapter_id: Internal ID for the adapter being tuned.
            continual_learning_round: Current federated/continual round.
            resume_checkpoint: Path to an existing checkpoint directory if resuming.

        Returns:
            The final TrainingCheckpoint metadata, or None if interrupted before saving.
        """
        self._stop_requested = False
        self._early_stopping.reset()
        self._metrics_service.clear()

        # Set seed
        torch.manual_seed(config.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(config.seed)

        model.train()

        # Prepare trainable parameters
        trainable_params = [p for p in model.parameters() if p.requires_grad]
        optimizer = self._opt_service.create_optimizer(trainable_params, config)

        total_steps = len(train_dataloader) * config.epochs
        scheduler = self._sched_service.create_scheduler(optimizer, config, total_steps)

        if resume_checkpoint:
            self._checkpoint_service.load_states(resume_checkpoint, optimizer, scheduler)

        self._training_monitor.start(total_steps)
        global_step = 0
        best_checkpoint = None

        start_time = time.perf_counter()

        for epoch in range(config.epochs):
            if self._stop_requested:
                break

            epoch_loss = 0.0

            for step, batch in enumerate(train_dataloader):
                if self._stop_requested:
                    break  # type: ignore

                # We assume the batch is a dict of tensors already on the correct device
                # and the model returns an object with a 'loss' attribute.
                # Since we don't have a real dataset implementation yet, we expect standard HF inputs.
                outputs = model(**batch)
                loss = outputs.loss

                self._grad_manager.backward(loss, config)

                if (step + 1) % config.gradient_accumulation_steps == 0:
                    stats = self._grad_manager.step(model, optimizer, config)
                    scheduler.step()
                    global_step += 1

                    self._training_monitor.update(global_step, epoch + (step / len(train_dataloader)))

                    # Hardware limit enforcement
                    if not self._resource_monitor.check_limits():
                        self._logger.warning("Resource limits exceeded. Triggering safe stop.")
                        self.request_stop()
                        break

                    # Checkpoint saving
                    if global_step % config.checkpoint_interval == 0:
                        _ = self._checkpoint_service.save_checkpoint(
                            model, optimizer, scheduler, adapter_id, epoch +
                            (step / len(train_dataloader)), continual_learning_round
                        )

                epoch_loss += loss.item()

            avg_train_loss = epoch_loss / len(train_dataloader) if len(train_dataloader) > 0 else 0.0

            # Validation Phase
            avg_val_loss = None
            if val_dataloader is not None and not self._stop_requested:
                model.eval()
                val_loss = 0.0
                with torch.no_grad():
                    for batch in val_dataloader:
                        outputs = model(**batch)
                        val_loss += outputs.loss.item()
                avg_val_loss = val_loss / len(val_dataloader) if len(val_dataloader) > 0 else 0.0
                model.train()

                is_best, should_stop = self._early_stopping.step(avg_val_loss)
                if is_best:
                    best_checkpoint = self._checkpoint_service.save_checkpoint(
                        model, optimizer, scheduler, adapter_id, float(epoch + 1), continual_learning_round
                    )

                if should_stop:
                    self.request_stop()

            # Record Metrics
            resources = self._resource_monitor.get_resource_usage()
            metrics = TrainingMetrics(
                epoch=float(epoch + 1),
                training_loss=avg_train_loss,
                validation_loss=avg_val_loss,
                accuracy=None,
                learning_rate=optimizer.param_groups[0]["lr"],
                gradient_norm=stats.get("grad_norm", 0.0) if 'stats' in locals() else 0.0,
                gpu_memory_mb=resources["gpu_memory_used_mb"],
                cpu_memory_mb=resources["ram_used_mb"],
                throughput=self._training_monitor.get_status().get("throughput_steps_per_sec", 0.0),
                elapsed_time_s=time.perf_counter() - start_time
            )
            self._metrics_service.record_metrics(metrics)

        self._training_monitor.stop()

        # Final checkpoint if not stopped early or if we don't have a best
        if best_checkpoint is None and not self._stop_requested:
            best_checkpoint = self._checkpoint_service.save_checkpoint(
                model, optimizer, scheduler, adapter_id, float(config.epochs), continual_learning_round
            )

        return best_checkpoint

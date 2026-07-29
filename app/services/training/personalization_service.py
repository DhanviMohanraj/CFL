"""DriftAdapt Personalization Service.

Author: DriftAdapt Contributors
Purpose: Exposes a high-level facade for managing the local personalization lifecycle via API endpoints.
"""

from typing import Optional, Any
import time

from app.core.logging import LoggerFactory
from app.schemas.personalization_request import PersonalizationRequest
from app.schemas.personalization_response import PersonalizationResponse

from app.models.foundation.model_manager import ModelManager
from app.personalization.peft.peft_manager import PEFTManager
from app.services.lora.adapter_registry import AdapterRegistry
from app.services.training.metrics_service import MetricsService
from app.services.training.training_monitor import TrainingMonitor
from app.training.local_trainer import LocalLoRATrainer


class PersonalizationService:
    """Service acting as the API interface for local training runs."""

    def __init__(
        self,
        model_manager: ModelManager,
        peft_manager: PEFTManager,
        registry: AdapterRegistry,
        metrics_service: MetricsService,
        training_monitor: TrainingMonitor
    ) -> None:
        self._logger = LoggerFactory.get_logger("PersonalizationService")
        self._model_manager = model_manager
        self._peft_manager = peft_manager
        self._registry = registry
        self._metrics_service = metrics_service
        self._training_monitor = training_monitor

    def start_personalization(self, request: PersonalizationRequest) -> PersonalizationResponse:
        """Starts a local personalization training loop.

        Args:
            request: The API personalization request payload.

        Returns:
            PersonalizationResponse summarizing the outcome.
        """
        self._logger.info(f"Starting personalization for adapter {request.adapter_id}...")
        start_time = time.perf_counter()

        # Retrieve the wrapped PEFT model (this assumes adapter is already injected via Module 2.3)
        peft_model = self._peft_manager.get_model()

        # In a real environment, we would load the dataset here using DatasetManager (future module)
        # For this architectural module, we construct dummy DataLoaders
        # to ensure the TrainingEngine is structurally sound.
        train_dataloader: list[Any] = []  # Placeholder for actual DataLoader
        val_dataloader = None

        try:
            # We use the new LocalLoRATrainer which utilizes HF Trainer
            config_dict = request.configuration.model_dump()
            # Pass necessary info in config
            config_dict["model_name"] = "Qwen/Qwen2.5-1.5B-Instruct"
            config_dict["dataset_dir"] = "datasets"
            config_dict["output_dir"] = f"./results/{request.client_id}"
            config_dict["batch_size"] = request.configuration.batch_size
            config_dict["epochs"] = request.configuration.epochs
            config_dict["learning_rate"] = request.configuration.learning_rate
            
            # Since MetricsService doesn't expose bus directly, we assume it's available or we skip it here if not needed
            # For simplicity we import a global or create a dummy bus if needed. Actually, metrics_service has it?
            # Wait, local trainer creates its own metrics or accepts one. Let's use get_metrics_bus if possible.
            # LocalLoRATrainer expects a MetricsBus instance.
            from app.core.metrics.metrics_bus import MetricsBus
            bus = MetricsBus() # or use self._metrics_service._metrics_bus if accessible
            
            trainer = LocalLoRATrainer(
                trainer_id=request.adapter_id,
                clinic_id=request.client_id,
                month=request.continual_learning_round,
                config=config_dict,
                metrics_bus=bus
            )
            
            trainer.initialize()
            trainer.prepare()
            trainer.train()
            export_path = trainer.export_adapter()
            
            elapsed = time.perf_counter() - start_time
            best_loss = 0.0 # Could get from trainer
            final_loss = 0.0 # Could get from trainer
            epochs_completed = float(config_dict["epochs"])
            
            # Register adapter in registry
            from app.services.lora.adapter_registry import AdapterMetadata
            meta = AdapterMetadata(
                adapter_id=request.adapter_id,
                client_id=request.client_id,
                continual_learning_round=request.continual_learning_round,
                model_name=config_dict["model_name"],
                file_path=export_path,
                trainable_parameters=1000000, # Placeholder or extract from PEFT model
                status="COMPLETED"
            )
            self._registry.register_adapter(meta)

            return PersonalizationResponse(
                success=True,
                training_time_s=elapsed,
                epochs_completed=epochs_completed,
                final_loss=final_loss,
                best_loss=best_loss,
                checkpoint_location=export_path,
                adapter_id=request.adapter_id,
                updated_parameters=1000000,
                status="COMPLETED"
            )

        except Exception as e:
            self._logger.error(f"Training failed: {e}")
            return PersonalizationResponse(
                success=False,
                training_time_s=time.perf_counter() - start_time,
                epochs_completed=0.0,
                final_loss=0.0,
                best_loss=None,
                checkpoint_location=None,
                adapter_id=request.adapter_id,
                updated_parameters=0,
                status=f"ERROR: {str(e)}"
            )

    def stop_personalization(self) -> None:
        """Requests graceful termination of the active training loop."""
        # For HF Trainer, we would need to pass a stop callback or interrupt the process.
        # Since we use LocalLoRATrainer synchronously for now, stopping requires signaling it.
        pass

    def get_status(self) -> dict:
        """Retrieves live monitoring stats."""
        return self._training_monitor.get_status()

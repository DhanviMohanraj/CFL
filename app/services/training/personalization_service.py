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
from app.services.training.training_engine import TrainingEngine
from app.services.training.metrics_service import MetricsService
from app.services.training.training_monitor import TrainingMonitor


class PersonalizationService:
    """Service acting as the API interface for local training runs."""

    def __init__(
        self,
        model_manager: ModelManager,
        peft_manager: PEFTManager,
        registry: AdapterRegistry,
        training_engine: TrainingEngine,
        metrics_service: MetricsService,
        training_monitor: TrainingMonitor
    ) -> None:
        self._logger = LoggerFactory.get_logger("PersonalizationService")
        self._model_manager = model_manager
        self._peft_manager = peft_manager
        self._registry = registry
        self._training_engine = training_engine
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
            checkpoint = self._training_engine.run(
                model=peft_model,
                train_dataloader=train_dataloader,  # type: ignore
                val_dataloader=val_dataloader,
                config=request.configuration,
                adapter_id=request.adapter_id,
                continual_learning_round=request.continual_learning_round,
                resume_checkpoint=request.resume_checkpoint
            )

            elapsed = time.perf_counter() - start_time
            best_loss = self._metrics_service.get_best_loss()

            history = self._metrics_service.get_history()
            final_loss = history[-1].training_loss if history else 0.0
            epochs_completed = history[-1].epoch if history else 0.0

            adapter_meta = self._registry.get_adapter(request.adapter_id)
            updated_params = adapter_meta.trainable_parameters if adapter_meta else 0

            if checkpoint:
                return PersonalizationResponse(
                    success=True,
                    training_time_s=elapsed,
                    epochs_completed=epochs_completed,
                    final_loss=final_loss,
                    best_loss=best_loss,
                    checkpoint_location=checkpoint.file_path,
                    adapter_id=request.adapter_id,
                    updated_parameters=updated_params,
                    status="COMPLETED"
                )
            else:
                return PersonalizationResponse(
                    success=False,
                    training_time_s=elapsed,
                    epochs_completed=epochs_completed,
                    final_loss=final_loss,
                    best_loss=best_loss,
                    checkpoint_location=None,
                    adapter_id=request.adapter_id,
                    updated_parameters=updated_params,
                    status="INTERRUPTED OR FAILED"
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
        self._training_engine.request_stop()

    def get_status(self) -> dict:
        """Retrieves live monitoring stats."""
        return self._training_monitor.get_status()

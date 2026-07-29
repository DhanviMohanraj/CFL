"""DriftAdapt Service Container Module.

Author: DriftAdapt Contributors
Purpose: Provides a centralized, thread-safe service container for managing singleton system services.
Future Integration: Injected into FastAPI routes via dependency injection in app/dependencies.py.
"""

import threading
import time
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.lora.adapter_registry import AdapterRegistry
    from app.services.lora.metadata_service import MetadataService
    from app.services.lora.adapter_initializer import AdapterInitializer
    
    from app.services.training.optimizer_service import OptimizerService
    from app.services.training.scheduler_service import SchedulerService
    from app.services.training.checkpoint_service import CheckpointService
    from app.services.training.training_monitor import TrainingMonitor
    from app.services.training.gradient_manager import GradientManager
    from app.services.training.personalization_service import PersonalizationService
    from app.services.training.metrics_service import MetricsService as TrainingMetricsService
    from app.services.training.early_stopping import EarlyStoppingService
    from app.services.training.resource_monitor import ResourceMonitor
    from app.services.training.training_engine import TrainingEngine

from app.core.config import ConfigManager
from app.core.device import DeviceManager
from app.core.logging import LoggerFactory
from app.core.metrics import MetricsBus
from app.core.runtime import EnvironmentManager, RuntimeManager
from app.core.seed import SeedManager
from app.models.foundation import ModelManager


class ServiceContainer:
    """Centralized Dependency Injection Container for DriftAdapt application services."""

    _instance: Optional["ServiceContainer"] = None
    _lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> "ServiceContainer":
        """Thread-safe singleton instantiation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initializes service container handles and state flags."""
        if getattr(self, "_initialized", False):
            return

        self._start_time: float = time.time()
        self._is_ready: bool = False
        self._lock = threading.Lock()

        # Services initialized lazily or on container creation
        self._config_manager: Optional[ConfigManager] = None
        self._metrics_bus: Optional[MetricsBus] = None
        self._device_manager: Optional[DeviceManager] = None
        self._runtime_manager: Optional[RuntimeManager] = None
        self._model_manager: Optional[ModelManager] = None
        
        # Module 2.3 LoRA API Services
        from app.services.lora.adapter_registry import AdapterRegistry
        from app.services.lora.metadata_service import MetadataService
        from app.services.lora.adapter_initializer import AdapterInitializer
        
        self._lora_registry: Optional[AdapterRegistry] = None
        self._lora_metadata_service: Optional[MetadataService] = None
        self._lora_adapter_initializer: Optional[AdapterInitializer] = None
        
        # Module 2.4 Training Services
        from app.services.training.optimizer_service import OptimizerService
        from app.services.training.scheduler_service import SchedulerService
        from app.services.training.checkpoint_service import CheckpointService
        from app.services.training.training_monitor import TrainingMonitor
        from app.services.training.gradient_manager import GradientManager
        from app.services.training.personalization_service import PersonalizationService
        from app.services.training.metrics_service import MetricsService as TrainingMetricsService
        from app.services.training.early_stopping import EarlyStoppingService
        from app.services.training.resource_monitor import ResourceMonitor
        from app.services.training.training_engine import TrainingEngine
        
        self._opt_service: Optional[OptimizerService] = None
        self._sched_service: Optional[SchedulerService] = None
        self._checkpoint_service: Optional[CheckpointService] = None
        self._training_monitor: Optional[TrainingMonitor] = None
        self._grad_manager: Optional[GradientManager] = None
        self._pers_service: Optional[PersonalizationService] = None
        self._training_metrics_service: Optional[TrainingMetricsService] = None
        self._early_stopping: Optional[EarlyStoppingService] = None
        self._resource_monitor: Optional[ResourceMonitor] = None
        self._training_engine: Optional[TrainingEngine] = None
        
        # Module 2.5 Federation Services
        from app.services.federation.update_extractor import UpdateExtractor
        from app.services.federation.compression_service import CompressionService
        from app.services.federation.encryption_service import EncryptionService
        from app.services.federation.checksum_service import ChecksumService
        from app.services.federation.update_packager import UpdatePackager
        from app.services.federation.bandwidth_optimizer import BandwidthOptimizer
        from app.services.federation.retry_manager import RetryManager
        from app.services.federation.transmission_logger import TransmissionLogger
        from app.services.federation.transmission_service import TransmissionService
        from app.services.federation.upload_queue import UploadQueue

        self._update_extractor: Optional[UpdateExtractor] = None
        self._compression_service: Optional[CompressionService] = None
        self._encryption_service: Optional[EncryptionService] = None
        self._checksum_service: Optional[ChecksumService] = None
        self._update_packager: Optional[UpdatePackager] = None
        self._bandwidth_optimizer: Optional[BandwidthOptimizer] = None
        self._retry_manager: Optional[RetryManager] = None
        self._transmission_logger: Optional[TransmissionLogger] = None
        self._transmission_service: Optional[TransmissionService] = None
        self._upload_queue: Optional[UploadQueue] = None

        # Module 2.6 Aggregation Services
        from app.services.aggregation.update_validator import UpdateValidator
        from app.services.aggregation.update_filter import UpdateFilter
        from app.services.aggregation.conflict_detector import ConflictDetector
        from app.services.aggregation.adapter_merger import AdapterMerger
        from app.services.aggregation.version_manager import VersionManager
        from app.services.aggregation.aggregation_history import AggregationHistory
        from app.services.aggregation.aggregation_registry import AggregationRegistry
        from app.services.aggregation.aggregation_metrics import AggregationMetrics
        from app.services.aggregation.aggregation_engine import AggregationEngine
        
        self._update_validator: Optional[UpdateValidator] = None
        self._update_filter: Optional[UpdateFilter] = None
        self._conflict_detector: Optional[ConflictDetector] = None
        self._adapter_merger: Optional[AdapterMerger] = None
        self._version_manager: Optional[VersionManager] = None
        self._aggregation_history: Optional[AggregationHistory] = None
        self._aggregation_registry: Optional[AggregationRegistry] = None
        self._aggregation_metrics: Optional[AggregationMetrics] = None
        self._aggregation_engine: Optional[AggregationEngine] = None

        # Module 2.7 Inference Services
        from app.services.inference.adapter_loader import AdapterLoader
        from app.services.inference.adapter_switcher import AdapterSwitcher
        from app.services.inference.adapter_registry import AdapterRegistry
        from app.services.inference.cache_manager import CacheManager
        from app.services.inference.prompt_processor import PromptProcessor
        from app.services.inference.tokenizer_service import TokenizerService
        from app.services.inference.generation_service import GenerationService
        from app.services.inference.streaming_service import StreamingService
        from app.services.inference.response_formatter import ResponseFormatter
        from app.services.inference.inference_history_manager import InferenceHistoryManager
        from app.services.inference.inference_metrics import InferenceMetrics
        from app.services.inference.inference_validator import InferenceValidator
        from app.services.inference.inference_engine import InferenceEngine
        
        self._inference_adapter_loader: Optional[AdapterLoader] = None
        self._inference_adapter_switcher: Optional[AdapterSwitcher] = None
        self._inference_adapter_registry: Optional[AdapterRegistry] = None
        self._inference_cache_manager: Optional[CacheManager] = None
        self._inference_prompt_processor: Optional[PromptProcessor] = None
        self._inference_tokenizer_service: Optional[TokenizerService] = None
        self._inference_generation_service: Optional[GenerationService] = None
        self._inference_streaming_service: Optional[StreamingService] = None
        self._inference_response_formatter: Optional[ResponseFormatter] = None
        self._inference_history_manager: Optional[InferenceHistoryManager] = None
        self._inference_metrics: Optional[InferenceMetrics] = None
        self._inference_validator: Optional[InferenceValidator] = None
        self._inference_engine: Optional[InferenceEngine] = None

        # Module 2.8 Validation & Benchmarking Services
        from app.services.validation.model_integrity_checker import ModelIntegrityChecker
        from app.services.validation.adapter_validator import AdapterValidator
        from app.services.validation.inference_validator import InferenceValidator as ValInferenceValidator
        from app.services.validation.latency_benchmark import LatencyBenchmark
        from app.services.validation.throughput_benchmark import ThroughputBenchmark
        from app.services.validation.memory_profiler import MemoryProfiler
        from app.services.validation.adapter_benchmark import AdapterBenchmark
        from app.services.validation.system_health_monitor import SystemHealthMonitor
        from app.services.validation.validation_report_generator import ValidationReportGenerator
        from app.services.validation.benchmark_report_generator import BenchmarkReportGenerator
        from app.services.validation.metrics_collector import MetricsCollector as ValMetricsCollector
        from app.services.validation.validation_history import ValidationHistory
        from app.services.validation.validation_registry import ValidationRegistry
        from app.services.validation.benchmark_engine import BenchmarkEngine
        from app.services.validation.validation_engine import ValidationEngine
        
        self._val_model_integrity_checker: Optional[ModelIntegrityChecker] = None
        self._val_adapter_validator: Optional[AdapterValidator] = None
        self._val_inference_validator: Optional[ValInferenceValidator] = None
        self._val_latency_benchmark: Optional[LatencyBenchmark] = None
        self._val_throughput_benchmark: Optional[ThroughputBenchmark] = None
        self._val_memory_profiler: Optional[MemoryProfiler] = None
        self._val_adapter_benchmark: Optional[AdapterBenchmark] = None
        self._val_system_health_monitor: Optional[SystemHealthMonitor] = None
        self._val_report_generator: Optional[ValidationReportGenerator] = None
        self._val_benchmark_report_generator: Optional[BenchmarkReportGenerator] = None
        self._val_metrics_collector: Optional[ValMetricsCollector] = None
        self._val_history: Optional[ValidationHistory] = None
        self._val_registry: Optional[ValidationRegistry] = None
        self._val_benchmark_engine: Optional[BenchmarkEngine] = None
        self._val_validation_engine: Optional[ValidationEngine] = None

        self._initialized = True

    @property
    def start_time(self) -> float:
        """Returns application startup timestamp."""
        return self._start_time

    @property
    def is_ready(self) -> bool:
        """Returns True if application startup sequence has completed successfully."""
        return self._is_ready

    def mark_ready(self, ready: bool = True) -> None:
        """Sets readiness status flag."""
        with self._lock:
            self._is_ready = ready

    def get_uptime_seconds(self) -> float:
        """Calculates current application running time in seconds."""
        return round(time.time() - self._start_time, 2)

    def config_manager(self) -> ConfigManager:
        """Retrieves ConfigManager singleton."""
        if self._config_manager is None:
            self._config_manager = ConfigManager()
        return self._config_manager

    def metrics_bus(self) -> MetricsBus:
        """Retrieves MetricsBus singleton."""
        if self._metrics_bus is None:
            self._metrics_bus = MetricsBus()
        return self._metrics_bus

    def device_manager(self) -> DeviceManager:
        """Retrieves DeviceManager singleton."""
        if self._device_manager is None:
            self._device_manager = DeviceManager()
        return self._device_manager

    def runtime_manager(self) -> RuntimeManager:
        """Retrieves RuntimeManager singleton."""
        if self._runtime_manager is None:
            self._runtime_manager = RuntimeManager()
        return self._runtime_manager

    def model_manager(self) -> ModelManager:
        """Returns the ModelManager instance."""
        if self._model_manager is None:
            self._model_manager = ModelManager(self.config_manager())
        return self._model_manager
        
    def lora_registry(self) -> "AdapterRegistry":
        """Returns the LoRA AdapterRegistry instance."""
        if self._lora_registry is None:
            from app.services.lora.adapter_registry import AdapterRegistry
            self._lora_registry = AdapterRegistry()
        return self._lora_registry
        
    def lora_metadata_service(self) -> "MetadataService":
        """Returns the LoRA MetadataService instance."""
        if self._lora_metadata_service is None:
            from app.services.lora.metadata_service import MetadataService
            self._lora_metadata_service = MetadataService(self.lora_registry())
        return self._lora_metadata_service
        
    def lora_adapter_initializer(self) -> "AdapterInitializer":
        """Returns the LoRA AdapterInitializer instance."""
        if self._lora_adapter_initializer is None:
            from app.services.lora.adapter_initializer import AdapterInitializer
            self._lora_adapter_initializer = AdapterInitializer(
                model_manager=self.model_manager(),
                registry=self.lora_registry()
            )
        return self._lora_adapter_initializer

    def training_metrics_service(self) -> "TrainingMetricsService":
        if self._training_metrics_service is None:
            from app.services.training.metrics_service import MetricsService as TrainingMetricsService
            self._training_metrics_service = TrainingMetricsService()
        return self._training_metrics_service

    def training_monitor(self) -> "TrainingMonitor":
        if self._training_monitor is None:
            from app.services.training.training_monitor import TrainingMonitor
            self._training_monitor = TrainingMonitor()
        return self._training_monitor

    def resource_monitor(self) -> "ResourceMonitor":
        if self._resource_monitor is None:
            from app.services.training.resource_monitor import ResourceMonitor
            self._resource_monitor = ResourceMonitor()
        return self._resource_monitor

    def early_stopping(self) -> "EarlyStoppingService":
        if self._early_stopping is None:
            from app.services.training.early_stopping import EarlyStoppingService
            self._early_stopping = EarlyStoppingService()
        return self._early_stopping

    def checkpoint_service(self) -> "CheckpointService":
        if self._checkpoint_service is None:
            from app.services.training.checkpoint_service import CheckpointService
            self._checkpoint_service = CheckpointService()
        return self._checkpoint_service

    def gradient_manager(self) -> "GradientManager":
        if self._grad_manager is None:
            from app.services.training.gradient_manager import GradientManager
            self._grad_manager = GradientManager()
        return self._grad_manager

    def optimizer_service(self) -> "OptimizerService":
        if self._opt_service is None:
            from app.services.training.optimizer_service import OptimizerService
            self._opt_service = OptimizerService()
        return self._opt_service

    def scheduler_service(self) -> "SchedulerService":
        if self._sched_service is None:
            from app.services.training.scheduler_service import SchedulerService
            self._sched_service = SchedulerService()
        return self._sched_service

    def training_engine(self) -> "TrainingEngine":
        if self._training_engine is None:
            from app.services.training.training_engine import TrainingEngine
            self._training_engine = TrainingEngine(
                optimizer_service=self.optimizer_service(),
                scheduler_service=self.scheduler_service(),
                gradient_manager=self.gradient_manager(),
                early_stopping=self.early_stopping(),
                checkpoint_service=self.checkpoint_service(),
                resource_monitor=self.resource_monitor(),
                training_monitor=self.training_monitor(),
                metrics_service=self.training_metrics_service()
            )
        return self._training_engine

    def personalization_service(self) -> "PersonalizationService":
        if self._pers_service is None:
            from app.services.training.personalization_service import PersonalizationService
            from app.personalization.peft.peft_manager import PEFTManager
            self._pers_service = PersonalizationService(
                model_manager=self.model_manager(),
                peft_manager=PEFTManager(),
                registry=self.lora_registry(),
                metrics_service=self.training_metrics_service(),
                training_monitor=self.training_monitor()
            )
        return self._pers_service

    @staticmethod
    def logger_factory() -> type[LoggerFactory]:
        """Returns LoggerFactory class reference."""
        return LoggerFactory

    @staticmethod
    def environment_manager() -> type[EnvironmentManager]:
        """Returns EnvironmentManager class reference."""
        return EnvironmentManager

    @staticmethod
    def seed_manager() -> type[SeedManager]:
        """Returns SeedManager class reference."""
        return SeedManager

    def get_services_status(self) -> Dict[str, str]:
        """Queries health status of registered container services."""
        return {
            "config_manager": "HEALTHY" if self._config_manager is not None else "UNINITIALIZED",
            "metrics_bus": "HEALTHY" if self._metrics_bus is not None else "UNINITIALIZED",
            "device_manager": "HEALTHY" if self._device_manager is not None else "UNINITIALIZED",
            "runtime_manager": "HEALTHY" if self._runtime_manager is not None else "UNINITIALIZED",
            "model_manager": "HEALTHY" if self._model_manager is not None else "UNINITIALIZED",
            "logger_factory": "HEALTHY",
            "environment_manager": "HEALTHY",
            "seed_manager": "HEALTHY",
        }

    def update_packager(self) -> Any:
        if self._update_packager is None:
            from app.services.federation.update_packager import UpdatePackager
            self._update_packager = UpdatePackager(
                compression_service=self.compression_service(),
                encryption_service=self.encryption_service(),
                checksum_service=self.checksum_service()
            )
        return self._update_packager

    def checksum_service(self) -> Any:
        if self._checksum_service is None:
            from app.services.federation.checksum_service import ChecksumService
            self._checksum_service = ChecksumService()
        return self._checksum_service

    def compression_service(self) -> Any:
        if self._compression_service is None:
            from app.services.federation.compression_service import CompressionService
            self._compression_service = CompressionService()
        return self._compression_service

    def encryption_service(self) -> Any:
        if self._encryption_service is None:
            from app.services.federation.encryption_service import EncryptionService
            self._encryption_service = EncryptionService(symmetric_key=b"12345678901234567890123456789012")
        return self._encryption_service

    def upload_queue(self) -> Any:
        if self._upload_queue is None:
            from app.services.federation.upload_queue import UploadQueue
            self._upload_queue = UploadQueue(transmission_service=self.transmission_service())
        return self._upload_queue
        
    def transmission_service(self) -> Any:
        if self._transmission_service is None:
            from app.services.federation.transmission_service import TransmissionService
            from app.services.federation.retry_manager import RetryManager
            from app.services.federation.transmission_logger import TransmissionLogger
            self._transmission_service = TransmissionService(
                retry_manager=RetryManager(),
                transmission_logger=TransmissionLogger()
            )
        return self._transmission_service

    def aggregation_update_validator(self) -> Any:
        if self._update_validator is None:
            from app.services.aggregation.update_validator import UpdateValidator
            self._update_validator = UpdateValidator(checksum_service=self.checksum_service())
        return self._update_validator
        
    def aggregation_update_filter(self) -> Any:
        if self._update_filter is None:
            from app.services.aggregation.update_filter import UpdateFilter
            self._update_filter = UpdateFilter()
        return self._update_filter
        
    def aggregation_conflict_detector(self) -> Any:
        if self._conflict_detector is None:
            from app.services.aggregation.conflict_detector import ConflictDetector
            self._conflict_detector = ConflictDetector()
        return self._conflict_detector
        
    def aggregation_adapter_merger(self) -> Any:
        if self._adapter_merger is None:
            from app.services.aggregation.adapter_merger import AdapterMerger
            self._adapter_merger = AdapterMerger()
        return self._adapter_merger
        
    def aggregation_version_manager(self) -> Any:
        if self._version_manager is None:
            from app.services.aggregation.version_manager import VersionManager
            self._version_manager = VersionManager()
        return self._version_manager
        
    def aggregation_history(self) -> Any:
        if self._aggregation_history is None:
            from app.services.aggregation.aggregation_history import AggregationHistory
            self._aggregation_history = AggregationHistory()
        return self._aggregation_history
        
    def aggregation_registry(self) -> Any:
        if self._aggregation_registry is None:
            from app.services.aggregation.aggregation_registry import AggregationRegistry
            self._aggregation_registry = AggregationRegistry()
        return self._aggregation_registry
        
    def aggregation_metrics(self) -> Any:
        if self._aggregation_metrics is None:
            from app.services.aggregation.aggregation_metrics import AggregationMetrics
            self._aggregation_metrics = AggregationMetrics()
        return self._aggregation_metrics
        
    def aggregation_engine(self) -> Any:
        if self._aggregation_engine is None:
            from app.services.aggregation.aggregation_engine import AggregationEngine
            self._aggregation_engine = AggregationEngine(
                update_validator=self.aggregation_update_validator(),
                update_filter=self.aggregation_update_filter(),
                conflict_detector=self.aggregation_conflict_detector(),
                adapter_merger=self.aggregation_adapter_merger(),
                version_manager=self.aggregation_version_manager(),
                aggregation_history=self.aggregation_history(),
                aggregation_registry=self.aggregation_registry(),
                aggregation_metrics=self.aggregation_metrics()
            )
        return self._aggregation_engine

    def inference_adapter_registry(self) -> Any:
        if self._inference_adapter_registry is None:
            from app.services.inference.adapter_registry import AdapterRegistry
            self._inference_adapter_registry = AdapterRegistry()
        return self._inference_adapter_registry
        
    def inference_adapter_loader(self) -> Any:
        if self._inference_adapter_loader is None:
            from app.services.inference.adapter_loader import AdapterLoader
            self._inference_adapter_loader = AdapterLoader(
                model_manager=self.model_manager(),
                adapter_registry=self.inference_adapter_registry()
            )
        return self._inference_adapter_loader
        
    def inference_adapter_switcher(self) -> Any:
        if self._inference_adapter_switcher is None:
            from app.services.inference.adapter_switcher import AdapterSwitcher
            self._inference_adapter_switcher = AdapterSwitcher(
                model_manager=self.model_manager(),
                adapter_registry=self.inference_adapter_registry()
            )
        return self._inference_adapter_switcher
        
    def inference_cache_manager(self) -> Any:
        if self._inference_cache_manager is None:
            from app.services.inference.cache_manager import CacheManager
            self._inference_cache_manager = CacheManager()
        return self._inference_cache_manager
        
    def inference_prompt_processor(self) -> Any:
        if self._inference_prompt_processor is None:
            from app.services.inference.prompt_processor import PromptProcessor
            self._inference_prompt_processor = PromptProcessor()
        return self._inference_prompt_processor
        
    def inference_tokenizer_service(self) -> Any:
        if self._inference_tokenizer_service is None:
            from app.services.inference.tokenizer_service import TokenizerService
            self._inference_tokenizer_service = TokenizerService(
                model_manager=self.model_manager()
            )
        return self._inference_tokenizer_service
        
    def inference_generation_service(self) -> Any:
        if self._inference_generation_service is None:
            from app.services.inference.generation_service import GenerationService
            self._inference_generation_service = GenerationService(
                model_manager=self.model_manager(),
                tokenizer_service=self.inference_tokenizer_service()
            )
        return self._inference_generation_service
        
    def inference_streaming_service(self) -> Any:
        if self._inference_streaming_service is None:
            from app.services.inference.streaming_service import StreamingService
            self._inference_streaming_service = StreamingService(
                model_manager=self.model_manager(),
                tokenizer_service=self.inference_tokenizer_service()
            )
        return self._inference_streaming_service
        
    def inference_response_formatter(self) -> Any:
        if self._inference_response_formatter is None:
            from app.services.inference.response_formatter import ResponseFormatter
            self._inference_response_formatter = ResponseFormatter()
        return self._inference_response_formatter
        
    def inference_history_manager(self) -> Any:
        if self._inference_history_manager is None:
            from app.services.inference.inference_history_manager import InferenceHistoryManager
            self._inference_history_manager = InferenceHistoryManager()
        return self._inference_history_manager
        
    def inference_metrics(self) -> Any:
        if self._inference_metrics is None:
            from app.services.inference.inference_metrics import InferenceMetrics
            self._inference_metrics = InferenceMetrics(metrics_bus=self.metrics_bus())
        return self._inference_metrics
        
    def inference_validator(self) -> Any:
        if self._inference_validator is None:
            from app.services.inference.inference_validator import InferenceValidator
            self._inference_validator = InferenceValidator(
                model_manager=self.model_manager(),
                adapter_registry=self.inference_adapter_registry()
            )
        return self._inference_validator
        
    def inference_engine(self) -> Any:
        if self._inference_engine is None:
            from app.services.inference.inference_engine import InferenceEngine
            self._inference_engine = InferenceEngine(
                adapter_loader=self.inference_adapter_loader(),
                adapter_switcher=self.inference_adapter_switcher(),
                adapter_registry=self.inference_adapter_registry(),
                cache_manager=self.inference_cache_manager(),
                prompt_processor=self.inference_prompt_processor(),
                tokenizer_service=self.inference_tokenizer_service(),
                generation_service=self.inference_generation_service(),
                streaming_service=self.inference_streaming_service(),
                response_formatter=self.inference_response_formatter(),
                history_manager=self.inference_history_manager(),
                metrics=self.inference_metrics(),
                validator=self.inference_validator()
            )
        return self._inference_engine

    def val_model_integrity_checker(self) -> Any:
        if self._val_model_integrity_checker is None:
            from app.services.validation.model_integrity_checker import ModelIntegrityChecker
            self._val_model_integrity_checker = ModelIntegrityChecker(self.model_manager())
        return self._val_model_integrity_checker
        
    def val_adapter_validator(self) -> Any:
        if self._val_adapter_validator is None:
            from app.services.validation.adapter_validator import AdapterValidator
            self._val_adapter_validator = AdapterValidator(self.inference_adapter_registry())
        return self._val_adapter_validator
        
    def val_inference_validator(self) -> Any:
        if self._val_inference_validator is None:
            from app.services.validation.inference_validator import InferenceValidator as ValInferenceValidator
            self._val_inference_validator = ValInferenceValidator(self.inference_engine())
        return self._val_inference_validator
        
    def val_latency_benchmark(self) -> Any:
        if self._val_latency_benchmark is None:
            from app.services.validation.latency_benchmark import LatencyBenchmark
            self._val_latency_benchmark = LatencyBenchmark(self.inference_engine())
        return self._val_latency_benchmark
        
    def val_throughput_benchmark(self) -> Any:
        if self._val_throughput_benchmark is None:
            from app.services.validation.throughput_benchmark import ThroughputBenchmark
            self._val_throughput_benchmark = ThroughputBenchmark(self.inference_engine())
        return self._val_throughput_benchmark
        
    def val_memory_profiler(self) -> Any:
        if self._val_memory_profiler is None:
            from app.services.validation.memory_profiler import MemoryProfiler
            self._val_memory_profiler = MemoryProfiler()
        return self._val_memory_profiler
        
    def val_adapter_benchmark(self) -> Any:
        if self._val_adapter_benchmark is None:
            from app.services.validation.adapter_benchmark import AdapterBenchmark
            self._val_adapter_benchmark = AdapterBenchmark(self.inference_adapter_loader(), self.inference_adapter_switcher())
        return self._val_adapter_benchmark
        
    def val_system_health_monitor(self) -> Any:
        if self._val_system_health_monitor is None:
            from app.services.validation.system_health_monitor import SystemHealthMonitor
            self._val_system_health_monitor = SystemHealthMonitor(
                self.val_memory_profiler(), self.model_manager(), self.inference_adapter_registry()
            )
        return self._val_system_health_monitor
        
    def val_report_generator(self) -> Any:
        if self._val_report_generator is None:
            from app.services.validation.validation_report_generator import ValidationReportGenerator
            self._val_report_generator = ValidationReportGenerator()
        return self._val_report_generator
        
    def val_benchmark_report_generator(self) -> Any:
        if self._val_benchmark_report_generator is None:
            from app.services.validation.benchmark_report_generator import BenchmarkReportGenerator
            self._val_benchmark_report_generator = BenchmarkReportGenerator()
        return self._val_benchmark_report_generator
        
    def val_metrics_collector(self) -> Any:
        if self._val_metrics_collector is None:
            from app.services.validation.metrics_collector import MetricsCollector as ValMetricsCollector
            self._val_metrics_collector = ValMetricsCollector(self.metrics_bus())
        return self._val_metrics_collector
        
    def val_history(self) -> Any:
        if self._val_history is None:
            from app.services.validation.validation_history import ValidationHistory
            self._val_history = ValidationHistory()
        return self._val_history
        
    def val_registry(self) -> Any:
        if self._val_registry is None:
            from app.services.validation.validation_registry import ValidationRegistry
            self._val_registry = ValidationRegistry()
        return self._val_registry
        
    def val_benchmark_engine(self) -> Any:
        if self._val_benchmark_engine is None:
            from app.services.validation.benchmark_engine import BenchmarkEngine
            self._val_benchmark_engine = BenchmarkEngine(
                self.val_latency_benchmark(),
                self.val_throughput_benchmark(),
                self.val_memory_profiler(),
                self.val_adapter_benchmark(),
                self.val_metrics_collector(),
                self.val_history(),
                self.val_registry()
            )
        return self._val_benchmark_engine
        
    def val_validation_engine(self) -> Any:
        if self._val_validation_engine is None:
            from app.services.validation.validation_engine import ValidationEngine
            self._val_validation_engine = ValidationEngine(
                self.val_model_integrity_checker(),
                self.val_adapter_validator(),
                self.val_inference_validator(),
                self.val_metrics_collector(),
                self.val_history(),
                self.val_registry()
            )
        return self._val_validation_engine

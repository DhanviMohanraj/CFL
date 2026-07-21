"""DriftAdapt Centralized MetricsBus.

Author: DriftAdapt Contributors
Purpose: Central node for publishing, storing, subscribing, exporting, and tracking system metrics.
Future Integration: Inherited and referenced by all client nodes, servers, and model wrappers.
"""

from pathlib import Path
import queue
import sys
import threading
import time
from typing import Dict, List, Optional, Any, Type

from app.core.config.config_manager import ConfigManager
from app.core.metrics.metric import Metric
from app.core.metrics.metric_types import MetricType
from app.core.metrics.metric_registry import MetricRegistry
from app.core.metrics.metric_store import MetricStore
from app.core.metrics.metric_events import (
    EventBus,
    MetricEvent,
    MetricPublished,
    MetricUpdated,
    ExperimentStarted,
    ExperimentFinished,
    EventHandler,
)
from app.core.metrics.publishers import MetricPublisher
from app.core.metrics.exceptions import MetricError, MetricValidationError
from loguru import logger


# Attempt optional imports for system telemetry
try:
    import psutil
except ImportError:
    psutil = None

try:
    import torch
except ImportError:
    torch = None


class MetricsBus(MetricPublisher):
    """Centralized, thread-safe metrics coordinator implementing MetricPublisher.

    Acts as the single point of entry for tracking all system, model, training,
    and federation metrics. Runs a background system resource telemetry thread.
    """

    _instance: Optional["MetricsBus"] = None
    _lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> "MetricsBus":
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, configs_dir: Optional[Path] = None) -> None:
        """Initializes the MetricsBus instance. Safe to run multiple times."""
        if getattr(self, "_initialized", False):
            return

        self._configs_dir = configs_dir
        self._registry = MetricRegistry()
        self._store = MetricStore()
        self._event_bus = EventBus()
        self._start_time = time.time()
        self._active_experiment: Optional[str] = None

        # Queue for async publishing
        self._async_queue: queue.Queue = queue.Queue()
        self._async_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Telemetry Thread
        self._telemetry_thread: Optional[threading.Thread] = None

        # Auto-register core system metric schemas
        self._register_default_schemas()

        # Start async worker daemon
        self._async_thread = threading.Thread(
            target=self._async_worker, daemon=True, name="MetricsBusAsyncWorker"
        )
        self._async_thread.start()

        # Start background resource telemetry daemon
        self._start_system_telemetry()

        self._initialized = True

    def _register_default_schemas(self) -> None:
        """Pre-registers standard telemetry schemas to pass validation checks."""
        # System resource schemas
        self._registry.register_schema(
            "system.cpu_percent",
            MetricType.CPU,
            "Percentage of global CPU utilization.",
        )
        self._registry.register_schema(
            "system.memory_percent",
            MetricType.MEMORY,
            "Percentage of global RAM memory utilization.",
        )
        self._registry.register_schema(
            "system.disk_percent",
            MetricType.SYSTEM,
            "Percentage of workspace disk usage.",
        )
        self._registry.register_schema(
            "system.gpu_memory_allocated_mb",
            MetricType.GPU,
            "CUDA memory currently allocated in Megabytes.",
        )
        self._registry.register_schema(
            "system.gpu_memory_reserved_mb",
            MetricType.GPU,
            "CUDA memory reserved in cache in Megabytes.",
        )
        self._registry.register_schema(
            "system.process_time_seconds",
            MetricType.SYSTEM,
            "Total CPU process time consumed by this run.",
        )
        self._registry.register_schema(
            "system.uptime_seconds",
            MetricType.SYSTEM,
            "Uptime duration of the MetricsBus in seconds.",
        )

        # Basic model metrics (placeholders for Module 2/3 validation)
        self._registry.register_schema(
            "train_loss", MetricType.LOSS, "Local client training loss value."
        )
        self._registry.register_schema(
            "val_loss", MetricType.LOSS, "Model validation loss value."
        )
        self._registry.register_schema(
            "val_accuracy",
            MetricType.ACCURACY,
            "Client evaluation classification accuracy.",
        )

    def register_schema(
        self, name: str, category: MetricType, description: str, metadata: Optional[dict] = None
    ) -> None:
        """Exposes schema registration of the internal registry."""
        self._registry.register_schema(name, category, description, metadata)

    def start_experiment(self, experiment_id: str) -> None:
        """Sets active experiment scope. Emits ExperimentStarted event."""
        with self._lock:
            self._active_experiment = experiment_id
        self._event_bus.notify(ExperimentStarted(experiment_id))

        # Log viaLoggerFactory integration point
        from app.core.logging import LoggerFactory

        LoggerFactory.get_logger("MetricsBus").info(
            f"Experiment run scope started: {experiment_id}"
        )

    def end_experiment(self) -> None:
        """Clears active experiment scope. Emits ExperimentFinished event."""
        exp_id = ""
        with self._lock:
            if self._active_experiment:
                exp_id = self._active_experiment
                self._active_experiment = None

        if exp_id:
            self._event_bus.notify(ExperimentFinished(exp_id))
            from app.core.logging import LoggerFactory

            LoggerFactory.get_logger("MetricsBus").info(
                f"Experiment run scope finished: {exp_id}"
            )

    def get_active_experiment(self) -> Optional[str]:
        """Returns the current active experiment ID."""
        return self._active_experiment

    # --- MetricPublisher Interface Implementation ---

    def validate_before_publish(self, metric: Metric) -> None:
        self._registry.validate_metric(metric)

    def publish(self, metric: Metric) -> None:
        """Synchronously publishes a metric.

        Validates, caches in memory, triggers events, and logs to metrics file.
        """
        # Automatically bind active experiment if not present in metric
        if not metric.experiment_id and self._active_experiment:
            metric.experiment_id = self._active_experiment

        # 1. Validate
        self.validate_before_publish(metric)

        # 2. Append to memory store
        self._store.append(metric)

        # 3. Notify subscribers
        self._event_bus.notify(MetricPublished(metric))

        # 4. Log to metrics split log
        from app.core.logging import LoggerFactory

        logger_inst = LoggerFactory.get_logger("MetricsBus")
        # Direct it to metrics.log by tagging extra context key 'metrics_log'
        logger_inst.info(
            f"Metric Published: {metric.name}={metric.value} (module={metric.module})",
            metrics_log=True,
        )

    def publish_batch(self, metrics: List[Metric]) -> None:
        """Publishes a list of metrics synchronously."""
        for m in metrics:
            self.publish(m)

    def publish_async(self, metric: Metric) -> None:
        """Pushes a metric onto the async processing queue."""
        if not metric.experiment_id and self._active_experiment:
            metric.experiment_id = self._active_experiment
        self._async_queue.put(metric)

    def _async_worker(self) -> None:
        """Background thread worker pulling items from async queue."""
        while not self._stop_event.is_set():
            try:
                # Poll with short timeout
                metric = self._async_queue.get(timeout=0.5)
                self.publish(metric)
                self._async_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                from loguru import logger

                logger.error(f"Error publishing metric asynchronously: {e}")

    # --- Query and Retrieval Interfaces ---

    def retrieve(self, name: str) -> List[Metric]:
        return self._store.retrieve(name)

    def latest(self, name: str) -> Optional[Metric]:
        return self._store.latest(name)

    def history(self, name: str) -> List[Any]:
        return self._store.history(name)

    def filter(
        self,
        name: Optional[str] = None,
        module: Optional[str] = None,
        client_id: Optional[str] = None,
        experiment_id: Optional[str] = None,
    ) -> List[Metric]:
        return self._store.filter(name, module, client_id, experiment_id)

    # --- Subscriptions Interface ---

    def subscribe(self, event_type: Type[MetricEvent], handler: EventHandler) -> None:
        self._event_bus.subscribe(event_type, handler)

    def unsubscribe(self, event_type: Type[MetricEvent], handler: EventHandler) -> None:
        self._event_bus.unsubscribe(event_type, handler)

    # --- Exporters Interface ---

    def export_all(self, csv_path: Path, json_path: Path) -> None:
        """Exports all cached metrics to both CSV and JSON. Thread-safe."""
        from app.core.metrics.exporters import CSVMetricExporter, JSONMetricExporter

        # Fetch current snapshot under lock
        with self._store._lock:
            all_metrics = list(self._store._metrics)

        CSVMetricExporter().export(all_metrics, csv_path)
        JSONMetricExporter().export(all_metrics, json_path)

    # --- Telemetry Collector Thread ---

    def _start_system_telemetry(self) -> None:
        """Spins up a daemon thread to collect system metrics periodically."""
        self._telemetry_thread = threading.Thread(
            target=self._telemetry_worker, daemon=True, name="MetricsBusTelemetryWorker"
        )
        self._telemetry_thread.start()

    def collect_system_metrics(self) -> None:
        """Manually triggers system resource metrics collection and publishing."""
        try:
            # 1. Global CPU/RAM Metrics (if psutil present)
            if psutil is not None:
                cpu_perc = psutil.cpu_percent()
                mem_info = psutil.virtual_memory()
                disk_info = psutil.disk_usage("/")

                self.publish(
                    Metric(
                        name="system.cpu_percent",
                        value=cpu_perc,
                        module="SystemCollector",
                    )
                )
                self.publish(
                    Metric(
                        name="system.memory_percent",
                        value=mem_info.percent,
                        module="SystemCollector",
                    )
                )
                self.publish(
                    Metric(
                        name="system.disk_percent",
                        value=disk_info.percent,
                        module="SystemCollector",
                    )
                )

            # 2. PyTorch GPU Telemetry (if CUDA active)
            if torch is not None and torch.cuda.is_available():
                alloc = torch.cuda.memory_allocated() / (1024 * 1024)
                res = torch.cuda.memory_reserved() / (1024 * 1024)
                self.publish(
                    Metric(
                        name="system.gpu_memory_allocated_mb",
                        value=alloc,
                        module="SystemCollector",
                    )
                )
                self.publish(
                    Metric(
                        name="system.gpu_memory_reserved_mb",
                        value=res,
                        module="SystemCollector",
                    )
                )

            # 3. Process time and Uptime
            process_time = time.process_time()
            uptime = time.time() - self._start_time

            self.publish(
                Metric(
                    name="system.process_time_seconds",
                    value=process_time,
                    module="SystemCollector",
                )
            )
            self.publish(
                Metric(
                    name="system.uptime_seconds",
                    value=uptime,
                    module="SystemCollector",
                )
            )

        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {e}")

    def _telemetry_worker(self) -> None:
        """Polls CPU, Memory, Disk, GPU usage, and publishes records to bus."""
        while not self._stop_event.is_set():
            # Collect metrics immediately on loop start
            self.collect_system_metrics()

            # Sleep for the configured interval
            try:
                # Fetch sampling interval from ConfigManager (defaults to 10s if missing)
                config = ConfigManager(configs_dir=self._configs_dir).get_config()
                interval = config.drift.sampling_interval  # Using sampling interval as period
                if interval <= 0:
                    interval = 10
            except Exception:
                interval = 10


            # Sleep split into small sleeps to terminate fast on shutdown
            sleep_steps = int(interval * 2)
            for _ in range(sleep_steps):
                if self._stop_event.is_set():
                    return
                time.sleep(0.5)



    def shutdown(self) -> None:
        """Stops background threads and blocks until queue is cleared."""
        self._stop_event.set()

        # Join async thread
        if self._async_thread and self._async_thread.is_alive():
            self._async_thread.join(timeout=2.0)

        # Join telemetry thread
        if self._telemetry_thread and self._telemetry_thread.is_alive():
            self._telemetry_thread.join(timeout=2.0)

        # Clear queue contents
        while not self._async_queue.empty():
            try:
                metric = self._async_queue.get_nowait()
                self.publish(metric)
                self._async_queue.task_done()
            except Exception:
                break

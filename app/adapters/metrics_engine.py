"""DriftAdapt Adapter Metrics Engine.

Author: DriftAdapt Contributors
Purpose: Singleton facade orchestrating metric collection, estimation, and export.
"""

import threading
from pathlib import Path
from typing import Optional

from app.adapters.communication_accounting import CommunicationAccounting
from app.adapters.metrics import AdapterMetricsPublisher
from app.adapters.metrics_collector import MetricsCollector
from app.adapters.metrics_exporter import MetricsExporter
from app.adapters.metrics_registry import MetricsRegistry
from app.adapters.performance_metrics import PerformanceMetricsCalculator
from app.adapters.storage_metrics import StorageMetricsCalculator
from app.core.config.config_manager import ConfigManager
from app.core.logging.logger_factory import LoggerFactory


class AdapterMetricsEngine:
    """Thread-safe Singleton facade for the metrics accounting subsystem."""
    
    _instance: Optional["AdapterMetricsEngine"] = None
    _lock = threading.RLock()
    
    def __new__(cls, *args, **kwargs) -> "AdapterMetricsEngine":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AdapterMetricsEngine, cls).__new__(cls)
        return cls._instance

    def __init__(self, configs_dir: Optional[Path] = None) -> None:
        if not hasattr(self, "_initialized"):
            with self._lock:
                if not hasattr(self, "_initialized"):
                    self._logger = LoggerFactory.get_logger("AdapterMetricsEngine")
                    self._registry = MetricsRegistry()
                    self._collector = MetricsCollector(self._registry)
                    
                    config = ConfigManager(configs_dir=configs_dir).get_config()
                    try:
                        metrics_config = getattr(config, "adapter_metrics", None)
                        if metrics_config:
                            export_dir = getattr(metrics_config, "export_directory", "reports/")
                            self._bandwidth_profile = getattr(metrics_config, "bandwidth_profile", "wifi")
                            self._compression_enabled = getattr(metrics_config, "compression_enabled", True)
                        else:
                            raise AttributeError()
                    except AttributeError:
                        export_dir = "reports/"
                        self._bandwidth_profile = "wifi"
                        self._compression_enabled = True
                        
                    self._exporter = MetricsExporter(self._registry, Path(export_dir))
                    self._storage_calc = StorageMetricsCalculator(self._registry)
                    self._perf_calc = PerformanceMetricsCalculator(self._registry)
                    self._comm_account = CommunicationAccounting(
                        profile_name=self._bandwidth_profile, 
                        compression_enabled=self._compression_enabled
                    )
                    
                    self._bus_publisher = AdapterMetricsPublisher()
                    self._initialized = True

    @property
    def collector(self) -> MetricsCollector:
        """Returns the ingestion point for metrics."""
        return self._collector
        
    @property
    def storage(self) -> StorageMetricsCalculator:
        """Returns the storage metrics calculator."""
        return self._storage_calc
        
    @property
    def performance(self) -> PerformanceMetricsCalculator:
        """Returns the performance metrics calculator."""
        return self._perf_calc
        
    @property
    def communication(self) -> CommunicationAccounting:
        """Returns the communication estimation engine."""
        return self._comm_account
        
    def export(self) -> None:
        """Exports metrics to JSON and CSV formats."""
        with self._lock:
            self._exporter.export_json()
            self._exporter.export_csv()
            
    def publish_to_bus(self) -> None:
        """Publishes derived metrics automatically to the centralized MetricsBus."""
        with self._lock:
            # Storage
            self._bus_publisher.publish("storage.total.bytes", self.storage.compute_total_storage_bytes())
            
            # Communication (Example from latest adapter if available)
            history = self._registry.get_adapter_history()
            if history:
                latest = history[-1]
                up = self.communication.estimate_upload(latest)
                down = self.communication.estimate_download(latest)
                self._bus_publisher.publish("communication.upload.bytes", up)
                self._bus_publisher.publish("communication.download.bytes", down)
                
            # Performance
            self._bus_publisher.publish("merge.duration.ms.avg", self.performance.average_merge_time())
            
    def reset(self) -> None:
        """Resets all collected metrics."""
        self._collector.reset()

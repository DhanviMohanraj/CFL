"""DriftAdapt Aggregation Engine.

Author: DriftAdapt Contributors
"""

import time
import hashlib
from typing import Dict, Any, List

import torch

from app.core.metrics.metrics_bus import MetricsBus
from app.aggregation.aggregation_manager import AggregationManager
from app.aggregation.aggregation_factory import AggregationFactory
from app.aggregation.aggregation_validator import AggregationValidator
from app.aggregation.aggregation_context import AggregationContext
from app.aggregation.aggregation_history import AggregationHistory
from app.aggregation.aggregation_registry import AggregationRegistry
from app.aggregation.aggregation_metrics import AggregationMetrics
from app.aggregation.aggregation_logger import AggregationLogger
from app.aggregation.aggregation_exceptions import AggregationError, AggregationInitializationError


class AggregationEngine:
    """Core engine for baseline federated aggregation algorithms."""
    
    def __init__(self, config: Dict[str, Any], metrics_bus: MetricsBus) -> None:
        self.config = config
        
        self.registry = AggregationRegistry()
        self.manager = AggregationManager(self.registry)
        
        self.history = AggregationHistory()
        self.metrics = AggregationMetrics(metrics_bus)
        
        self.validator = AggregationValidator(config)
        self.logger = None
        self.context = None
        
    def initialize(self, round_id: str, clients: List[str]) -> None:
        """Initializes the aggregation for a given round."""
        self.logger = AggregationLogger(round_id)
        
        alg_name = self.config.get("algorithm", "fedavg")
        self.manager.start_aggregation(round_id, alg_name, clients)
        
        self.context = AggregationContext(round_id, self.config, clients)
        self.metrics.publish_event("aggregation.started", {"round_id": round_id})
        self.logger.info(f"Aggregation initialized for round {round_id} with algorithm {alg_name}")
        
    def aggregate(self, round_id: str, adapter_paths: List[str]) -> str:
        """Executes the aggregation process and returns the global adapter path."""
        try:
            alg_name = self.config.get("algorithm", "fedavg")
            algorithm = AggregationFactory.get_algorithm(alg_name)
            
            # Mock loading of adapters
            adapter_state_dicts = []
            metadata = []
            for path in adapter_paths:
                sd = {"lora_A": torch.randn(10, 10), "lora_B": torch.randn(10, 10)}
                adapter_state_dicts.append(sd)
                meta = {"dataset_size": 100} # Mock metadata
                metadata.append(meta)
                
            self.metrics.publish_value("aggregation.adapter.count", len(adapter_paths))
            
            if self.config.get("validate_before_merge", True):
                val_start = time.time()
                self.validator.validate_before_merge(adapter_state_dicts)
                val_duration = time.time() - val_start
                self.metrics.publish_value("aggregation.validation.time", val_duration)
                
            start_time = time.time()
            global_state_dict = algorithm.aggregate(adapter_state_dicts, metadata, self.config)
            duration = time.time() - start_time
            
            if self.config.get("validate_after_merge", True):
                self.validator.validate_after_merge(global_state_dict)
                
            # Mock export
            global_adapter_path = f"exports/{round_id}_global_adapter.pt"
            
            checksum = hashlib.sha256(b"mock_global_data").hexdigest()
            version = f"v{round_id}"
            
            if self.config.get("save_history", True):
                self.history.record_aggregation(
                    round_id=round_id,
                    algorithm=alg_name,
                    clients=self.context.clients if self.context else [],
                    duration=duration,
                    version=version,
                    checksum=checksum,
                    metrics={"duration": duration}
                )
                
            self.manager.finish_aggregation(round_id, success=True, version=version, checksum=checksum)
            
            self.metrics.publish_event("aggregation.completed", {"round_id": round_id})
            self.metrics.publish_value("aggregation.duration", duration)
            self.metrics.publish_value("aggregation.output.version", version)
            
            if self.logger:
                self.logger.info("Aggregation completed successfully.")
                
            return global_adapter_path
            
        except Exception as e:
            self.manager.finish_aggregation(round_id, success=False)
            self.metrics.publish_event("aggregation.failed", {"round_id": round_id})
            if self.logger:
                self.logger.error(f"Aggregation failed: {e}")
            raise AggregationError(f"Aggregation failed: {e}") from e
            
    def status(self, round_id: str) -> str:
        meta = self.registry.lookup(round_id)
        return meta.status if meta else "UNKNOWN"

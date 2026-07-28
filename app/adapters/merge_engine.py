"""DriftAdapt Adapter Merge Engine.

Author: DriftAdapt Contributors
Purpose: Central orchestrator for baseline LoRA aggregation algorithms.
"""

import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.adapters.averaging import NaiveAverageMerge
from app.adapters.checksum import ChecksumEngine
from app.adapters.compatibility import CompatibilityChecker
from app.adapters.merge_exceptions import DuplicateAdapterError, InvalidMergeStrategy, MergeFailed
from app.adapters.merge_metadata import AdapterMergeMetadata
from app.adapters.merge_metrics import MergeMetricsPublisher
from app.adapters.merge_strategy import AdapterMergeStrategy
from app.adapters.merge_validator import MergeValidator
from app.adapters.serializer import AdapterSerializer
from app.adapters.state_utils import AdapterStateManager
from app.adapters.version_metadata import AdapterVersionMetadata
from app.core.config.config_manager import ConfigManager
from app.core.logging.logger_factory import LoggerFactory


class AdapterMergeEngine:
    """Thread-safe Singleton facade for orchestrating adapter merging."""
    
    _instance: Optional["AdapterMergeEngine"] = None
    _lock = threading.RLock()
    
    def __new__(cls, *args, **kwargs) -> "AdapterMergeEngine":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AdapterMergeEngine, cls).__new__(cls)
        return cls._instance

    def __init__(self, configs_dir: Optional[Path] = None) -> None:
        if not hasattr(self, "_initialized"):
            with self._lock:
                if not hasattr(self, "_initialized"):
                    self._logger = LoggerFactory.get_logger("AdapterMergeEngine")
                    self._metrics = MergeMetricsPublisher()
                    
                    config = ConfigManager(configs_dir=configs_dir).get_config()
                    try:
                        merge_config = getattr(config, "adapter_merge", None)
                        if merge_config:
                            self._default_strategy_name = getattr(merge_config, "default_strategy", "naive_average")
                            self._verify_checksum = getattr(merge_config, "verify_checksum", True)
                            self._strict_validation = getattr(merge_config, "strict_validation", True)
                            self._allow_duplicate_inputs = getattr(merge_config, "allow_duplicate_inputs", False)
                        else:
                            raise AttributeError()
                    except AttributeError:
                        self._default_strategy_name = "naive_average"
                        self._verify_checksum = True
                        self._strict_validation = True
                        self._allow_duplicate_inputs = False
                        
                    self._strategies: Dict[str, AdapterMergeStrategy] = {
                        "naive_average": NaiveAverageMerge()
                    }
                    
                    self._validator = MergeValidator()
                    self._compatibility = CompatibilityChecker()
                    self._serializer = AdapterSerializer()
                    self._state_manager = AdapterStateManager()
                    self._checksum_engine = ChecksumEngine()
                    self._initialized = True

    def register_strategy(self, strategy: AdapterMergeStrategy) -> None:
        """Registers a new merge strategy for future extensibility."""
        with self._lock:
            self._strategies[strategy.strategy_name()] = strategy
            self._logger.info(f"Registered strategy: {strategy.strategy_name()}")

    def _get_strategy(self, name: str) -> AdapterMergeStrategy:
        if name not in self._strategies:
            raise InvalidMergeStrategy(f"Strategy {name} is not supported.")
        return self._strategies[name]

    def validate_merge(
        self, states: List[Dict[str, Any]], version_metadata_list: List[AdapterVersionMetadata]
    ) -> None:
        """Validates that a merge is mathematically and structurally possible."""
        version_ids = [v.version_id for v in version_metadata_list]
        
        if not self._allow_duplicate_inputs and len(set(version_ids)) != len(version_ids):
            raise DuplicateAdapterError("Duplicate adapter IDs supplied to merge.")
            
        self._compatibility.verify_compatibility(version_metadata_list)
        
        if self._strict_validation:
            self._validator.validate_inputs(states, version_ids)

    def merge_states(
        self, 
        states: List[Dict[str, Any]], 
        version_metadata_list: List[AdapterVersionMetadata],
        strategy_name: Optional[str] = None,
        weights: Optional[List[float]] = None,
        communication_round: int = 1
    ) -> Tuple[Dict[str, Any], AdapterMergeMetadata]:
        """Core merge implementation logic.
        
        Args:
            states: The input list of LoRA state dictionaries.
            version_metadata_list: The metadata matching each state.
            strategy_name: Optional strategy to override default.
            weights: Optional weighting factors for strategies that support it.
            communication_round: The round being generated.
            
        Returns:
            A tuple containing (merged_state_dictionary, merge_metadata).
        """
        with self._lock:
            start_time = time.perf_counter()
            self._logger.info("Merge started")
            
            # Validation
            try:
                self.validate_merge(states, version_metadata_list)
            except Exception as e:
                self._metrics.publish("merge_failure", 1)
                self._logger.error(f"Validation failures: {e}")
                raise
                
            # Selection
            selected_strategy_name = strategy_name or self._default_strategy_name
            strategy = self._get_strategy(selected_strategy_name)
            self._logger.info(f"Strategy selected: {selected_strategy_name}")
            
            strategy.validate_inputs(states)
            
            if weights and not strategy.supports_weighting():
                self._logger.warning(f"Strategy {selected_strategy_name} does not support weighting. Weights ignored.")
                
            # Execution
            try:
                merged_state = strategy.merge(states, weights)
            except Exception as e:
                self._metrics.publish("merge_failure", 1)
                self._logger.error(f"Errors during strategy merge: {e}")
                raise MergeFailed(f"Strategy merge execution failed: {e}")
                
            # Integrity and Output Calculation
            output_adapter_id = str(uuid.uuid4())
            merge_id = f"merge_{output_adapter_id}"
            
            serialized_data = self._serializer.serialize(merged_state)
            checksum = self._checksum_engine.compute_checksum(serialized_data)
            out_size = len(serialized_data)
            out_params = self._state_manager.count_parameters(merged_state)
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            clinics = list(set([v.clinic_id for v in version_metadata_list]))
            versions = [v.version_id for v in version_metadata_list]
            
            metadata = AdapterMergeMetadata(
                merge_id=merge_id,
                strategy=selected_strategy_name,
                participating_clinics=clinics,
                participating_versions=versions,
                parameter_count=version_metadata_list[0].parameter_count,
                merged_parameter_count=out_params,
                communication_round=communication_round,
                checksum=checksum,
                merge_duration_ms=duration_ms,
                output_adapter_id=output_adapter_id
            )
            
            self._metrics.publish("merge_duration_ms", duration_ms)
            self._metrics.publish("merged_parameter_count", out_params)
            self._metrics.publish("input_adapter_count", len(states))
            self._metrics.publish("communication_payload_bytes", sum(v.adapter_size_bytes for v in version_metadata_list))
            self._metrics.publish("output_adapter_size", out_size)
            self._metrics.publish("merge_success", 1)
            self._metrics.publish("strategy_used", selected_strategy_name)
            
            self._logger.info(f"Merge completed. Output checksum: {checksum}. Merge duration: {duration_ms:.2f}ms")
            
            return merged_state, metadata
            
    def merge(self, *args, **kwargs) -> Tuple[Dict[str, Any], AdapterMergeMetadata]:
        """Alias for merge_states."""
        return self.merge_states(*args, **kwargs)

"""Aggregation Engine.

Author: DriftAdapt Contributors
Purpose: Central orchestrator for the entire federated aggregation lifecycle.
"""

import time
import hashlib
from typing import Dict, List, Optional, Any

from app.core.logging import LoggerFactory
from app.schemas.aggregation_request import AggregationRequest
from app.schemas.aggregation_result import AggregationResult
from app.schemas.client_update_record import ClientUpdateRecord
from app.schemas.global_adapter import GlobalAdapter
from app.schemas.aggregation_metadata import AggregationMetadata
from app.services.federation.metadata_builder import TORCH_VERSION

from app.services.aggregation.base_aggregator import BaseAggregator
from app.services.aggregation.fedavg_service import FedAvgService
from app.services.aggregation.weighted_fedavg import WeightedFedAvgService
from app.services.aggregation.update_validator import UpdateValidator
from app.services.aggregation.update_filter import UpdateFilter
from app.services.aggregation.conflict_detector import ConflictDetector
from app.services.aggregation.adapter_merger import AdapterMerger
from app.services.aggregation.version_manager import VersionManager
from app.services.aggregation.aggregation_history import AggregationHistory
from app.services.aggregation.aggregation_registry import AggregationRegistry
from app.services.aggregation.aggregation_metrics import AggregationMetrics


class AggregationEngine:
    """Orchestrates the complete federated learning aggregation pipeline."""
    
    def __init__(
        self,
        update_validator: UpdateValidator,
        update_filter: UpdateFilter,
        conflict_detector: ConflictDetector,
        adapter_merger: AdapterMerger,
        version_manager: VersionManager,
        aggregation_history: AggregationHistory,
        aggregation_registry: AggregationRegistry,
        aggregation_metrics: AggregationMetrics
    ) -> None:
        self._logger = LoggerFactory.get_logger("AggregationEngine")
        self._update_validator = update_validator
        self._update_filter = update_filter
        self._conflict_detector = conflict_detector
        self._adapter_merger = adapter_merger
        self._version_manager = version_manager
        self._aggregation_history = aggregation_history
        self._aggregation_registry = aggregation_registry
        self._aggregation_metrics = aggregation_metrics
        
        # Strategy pattern routing
        self._strategies: Dict[str, BaseAggregator] = {
            "fedavg": FedAvgService(),
            "weighted_fedavg": WeightedFedAvgService()
        }
        
        # In-memory staging area for incoming client updates prior to aggregation
        self._staging_records: Dict[str, ClientUpdateRecord] = {}
        self._staging_payloads: Dict[str, bytes] = {}

    def submit_client_update(self, record: ClientUpdateRecord, payload_bytes: bytes) -> bool:
        """Receives a client update and places it in the staging area."""
        self._logger.info(f"Received client update from {record.client_id} for round {record.personalization_round}.")
        self._staging_records[record.client_id] = record
        self._staging_payloads[record.client_id] = payload_bytes
        self._aggregation_registry.register_client(record.client_id)
        return True

    def run_aggregation(self, request: AggregationRequest) -> AggregationResult:
        """Executes the complete aggregation pipeline."""
        self._logger.info(f"Starting aggregation round {request.communication_round} using {request.aggregation_algorithm}.")
        start_time = time.perf_counter()
        
        try:
            # 1. Fetch staged updates
            if request.participating_clients:
                target_clients = set(request.participating_clients)
                staged = [r for cid, r in self._staging_records.items() if cid in target_clients]
            else:
                staged = list(self._staging_records.values())
                
            # 2. Detect high-level conflicts
            conflicts = self._conflict_detector.detect_conflicts(staged, request.communication_round)
            if conflicts:
                self._logger.warning(f"Conflicts detected prior to aggregation: {conflicts}")
                # We can choose to abort or proceed. For robustness, if structural conflicts exist, abort.
                if any("server is on round" in c for c in conflicts):
                    return self._build_failed_result(request, start_time, "Severe version conflict detected.")
                    
            # 3. Validation
            valid_records = []
            invalid_records = []
            for record in staged:
                payload = self._staging_payloads[record.client_id]
                if self._update_validator.validate_record(record, request.communication_round, payload):
                    valid_records.append(record)
                else:
                    invalid_records.append(record)
                    
            # 4. Filtering
            accepted, rejected = self._update_filter.filter_updates(valid_records, request.communication_round)
            invalid_records.extend(rejected)
            
            # 5. Check Minimum Thresholds
            if not self._update_filter.check_minimum_participation(accepted, request.minimum_clients):
                return self._build_failed_result(request, start_time, f"Insufficient valid clients (needed {request.minimum_clients}).")
                
            # 6. Retrieve algorithm strategy
            strategy = self._strategies.get(request.aggregation_algorithm)
            if not strategy:
                return self._build_failed_result(request, start_time, f"Unsupported algorithm: {request.aggregation_algorithm}")
                
            # 7. Merge Adapters
            accepted_payloads = [self._staging_payloads[r.client_id] for r in accepted]
            
            current_global = self._aggregation_registry.get_current_global_adapter()
            global_sd = current_global.state_dict if current_global else None
            
            merged_sd = self._adapter_merger.merge_adapters(
                updates=accepted,
                payloads=accepted_payloads,
                strategy=strategy,
                global_state_dict=global_sd
            )
            
            # 8. Construct New Global Adapter
            param_count = sum(t.numel() for t in merged_sd.values() if hasattr(t, "numel"))
            new_version = self._version_manager.generate_next_version(request.communication_round)
            
            metadata = AggregationMetadata(
                foundation_model_version="qwen-3b", # Mocked config resolution
                server_environment="linux",
                torch_version=TORCH_VERSION,
                total_participating_clients=len(self._aggregation_registry.get_registered_clients()),
                global_dataset_size_accumulated=sum(r.dataset_size for r in accepted),
                framework_versions={"peft": "0.10.0"}
            )
            
            # Create a pseudo-checksum for the state dict
            keys_hash = hashlib.sha256(",".join(sorted(merged_sd.keys())).encode()).hexdigest()
            
            global_adapter = GlobalAdapter(
                adapter_version=new_version,
                communication_round=request.communication_round,
                parameter_count=param_count,
                participating_clients=[r.client_id for r in accepted],
                creation_timestamp=time.time(),
                checksum=keys_hash,
                metadata=metadata,
                state_dict=merged_sd
            )
            
            self._aggregation_registry.register_global_adapter(global_adapter)
            
            # 9. Metrics & History
            duration = time.perf_counter() - start_time
            stats = self._aggregation_metrics.compute_statistics(
                accepted_updates=accepted,
                rejected_updates=invalid_records,
                aggregation_duration_s=duration,
                parameter_count=param_count
            )
            
            result = AggregationResult(
                success=True,
                communication_round=request.communication_round,
                aggregated_clients=[r.client_id for r in accepted],
                discarded_clients=[r.client_id for r in invalid_records],
                aggregation_duration=duration,
                algorithm_used=request.aggregation_algorithm,
                global_adapter_version=new_version,
                aggregation_statistics=stats
            )
            
            self._aggregation_history.record_aggregation(result)
            
            # Clear staging area (in a real system, you'd archive these)
            self._staging_records.clear()
            self._staging_payloads.clear()
            
            self._logger.info(f"Aggregation round {request.communication_round} completed successfully.")
            return result
            
        except Exception as e:
            self._logger.error(f"Critical aggregation failure: {str(e)}")
            return self._build_failed_result(request, time.perf_counter() - start_time, str(e))

    def _build_failed_result(self, request: AggregationRequest, duration: float, error_msg: str) -> AggregationResult:
        """Helper to construct a failure result."""
        result = AggregationResult(
            success=False,
            communication_round=request.communication_round,
            algorithm_used=request.aggregation_algorithm,
            aggregation_duration=duration,
            error_message=error_msg
        )
        self._aggregation_history.record_aggregation(result)
        return result
        
    def rollback(self, target_version: Optional[str] = None) -> bool:
        """Rolls back the global adapter to a previous version."""
        new_version = self._version_manager.rollback_version(target_version)
        if new_version:
            success = self._aggregation_registry.set_current_version(new_version)
            if success:
                self._aggregation_history.remove_latest()
            return success
        return False

import time
import flwr as fl
from typing import List, Tuple, Optional, Dict
from flwr.common import FitRes, Parameters, Scalar, ndarrays_to_parameters, parameters_to_ndarrays
from flwr.server.client_proxy import ClientProxy

from app.core.logging import LoggerFactory
from app.schemas.client_update_record import ClientUpdateRecord
from app.services.aggregation.conflict_detector import ConflictDetector

class DriftAdaptStrategy(fl.server.strategy.FedAvg):
    """Custom Flower Strategy for DriftAdapt that integrates existing conflict detection."""

    def __init__(self, conflict_detector: ConflictDetector, **kwargs):
        super().__init__(**kwargs)
        self._logger = LoggerFactory.get_logger("DriftAdaptStrategy")
        self._conflict_detector = conflict_detector

    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[BaseException],
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
        
        self._logger.info(f"Aggregating fit results for round {server_round}")

        if not results:
            return None, {}

        # Construct pseudo ClientUpdateRecords for our existing ConflictDetector
        updates = []
        for client_proxy, fit_res in results:
            # We assume node_id is available in client_proxy or we use cid
            record = ClientUpdateRecord(
                client_id=client_proxy.cid,
                personalization_round=server_round,
                local_epoch=1,
                dataset_size=fit_res.num_examples,
                checksum="mock_flower_checksum", # Flower natively handles transport integrity
                training_metrics=fit_res.metrics
            )
            updates.append(record)

        # Detect Conflicts
        conflicts = self._conflict_detector.detect_conflicts(updates, server_round)
        if conflicts:
            self._logger.warning(f"Conflicts detected in round {server_round}: {conflicts}")
            # In a strict environment, we could abort aggregation. Here we log and proceed.

        # Delegate the actual aggregation to Flower's standard FedAvg logic
        aggregated_parameters, metrics = super().aggregate_fit(server_round, results, failures)

        # In a real environment, we would also convert aggregated_parameters back to PyTorch
        # and save it to the AdapterRegistry.
        if aggregated_parameters is not None:
            self._logger.info(f"Successfully aggregated {len(results)} client models.")
            # Store in registry would happen here, or via a server-side callback

        return aggregated_parameters, metrics

"""Aggregation History Service.

Author: DriftAdapt Contributors
Purpose: Maintains a ledger of past aggregations and their corresponding metrics/results.
"""

from typing import List, Dict, Optional

from app.core.logging import LoggerFactory
from app.schemas.aggregation_result import AggregationResult


class AggregationHistory:
    """Stores the historical lineage of all federated aggregation events."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("AggregationHistory")
        # In-memory history ledger. In production, this would be a DB or append-only log.
        self._history: List[AggregationResult] = []

    def record_aggregation(self, result: AggregationResult) -> None:
        """Appends a new aggregation result to the history ledger."""
        self._history.append(result)
        self._logger.info(f"Recorded aggregation history for round {result.communication_round}.")

    def get_history(self) -> List[AggregationResult]:
        """Retrieves the full chronological aggregation history."""
        return self._history.copy()

    def get_round(self, round_num: int) -> Optional[AggregationResult]:
        """Retrieves a specific aggregation round by number."""
        for result in self._history:
            if result.communication_round == round_num:
                return result
        return None

    def remove_latest(self) -> Optional[AggregationResult]:
        """Removes and returns the latest record (used during rollback)."""
        if self._history:
            dropped = self._history.pop()
            self._logger.info(f"Removed aggregation history for round {dropped.communication_round}.")
            return dropped
        return None

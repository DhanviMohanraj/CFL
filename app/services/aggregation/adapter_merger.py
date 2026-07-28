"""Adapter Merger Service.

Author: DriftAdapt Contributors
Purpose: Orchestrates the loading of payload bytes into PyTorch state dictionaries and delegates to the aggregation strategy.
"""

import io
from typing import List, Dict, Any, Tuple, Optional

try:
    import torch
except ImportError:
    pass

from app.core.logging import LoggerFactory
from app.schemas.client_update_record import ClientUpdateRecord
from app.services.aggregation.base_aggregator import BaseAggregator


class AdapterMerger:
    """Manages the translation of raw payload bytes into PyTorch structures and invokes the math strategy."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("AdapterMerger")

    def _load_state_dict(self, payload_bytes: bytes) -> Dict[str, Any]:
        """Loads a state dict from raw bytes using torch.load.
        
        Args:
            payload_bytes: The serialized PyTorch dictionary.
            
        Returns:
            The loaded dictionary.
        """
        buffer = io.BytesIO(payload_bytes)
        try:
            state_dict = torch.load(buffer, map_location="cpu")
            if "lora_state_dict" in state_dict:
                return state_dict["lora_state_dict"]
            return state_dict
        except Exception as e:
            raise ValueError(f"Failed to load PyTorch state dict from bytes: {e}") from e

    def merge_adapters(
        self,
        updates: List[ClientUpdateRecord],
        payloads: List[bytes],
        strategy: BaseAggregator,
        global_state_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Loads payloads, extracts weights, and delegates to the aggregation strategy.
        
        Args:
            updates: The validated ClientUpdateRecords.
            payloads: The corresponding raw bytes for each update.
            strategy: The aggregation algorithm to apply.
            global_state_dict: Optional current global state dict.
            
        Returns:
            The newly aggregated global state dict.
        """
        if len(updates) != len(payloads):
            raise ValueError("Mismatched updates and payloads length.")
            
        self._logger.info(f"Loading {len(updates)} adapter payloads into memory for merging.")
        
        state_dicts: List[Dict[str, Any]] = []
        weights: List[float] = []
        
        for update, payload in zip(updates, payloads):
            try:
                sd = self._load_state_dict(payload)
                state_dicts.append(sd)
                
                # Weight resolution based on dataset_size vs base equal weight
                weight = update.update_weight
                if strategy.algorithm_name == "weighted_fedavg" and update.dataset_size > 0:
                    weight = float(update.dataset_size)
                    
                weights.append(weight)
                
            except Exception as e:
                self._logger.error(f"Failed to process payload for client {update.client_id}: {e}")
                # We could continue, but strictly we should raise if a payload is corrupt at this stage
                raise ValueError(f"Corrupt payload for client {update.client_id}") from e
                
        self._logger.info(f"Invoking {strategy.algorithm_name} strategy.")
        
        merged_state_dict = strategy.aggregate(
            state_dicts=state_dicts,
            weights=weights,
            global_state_dict=global_state_dict
        )
        
        return merged_state_dict

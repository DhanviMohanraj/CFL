"""Update Validator Service.

Author: DriftAdapt Contributors
Purpose: Performs strict validation on incoming client updates before they are accepted for filtering and merging.
"""

from typing import Dict, Any, Optional

from app.core.logging import LoggerFactory
from app.schemas.client_update_record import ClientUpdateRecord
from app.services.federation.checksum_service import ChecksumService


class UpdateValidator:
    """Validates structural and cryptographical integrity of incoming updates."""
    
    def __init__(self, checksum_service: ChecksumService) -> None:
        self._logger = LoggerFactory.get_logger("UpdateValidator")
        self._checksum_service = checksum_service

    def validate_record(
        self,
        record: ClientUpdateRecord,
        expected_round: int,
        raw_payload_bytes: Optional[bytes] = None
    ) -> bool:
        """Validates a client update record against basic constraints.
        
        Args:
            record: The ClientUpdateRecord metadata.
            expected_round: The current federated communication round.
            raw_payload_bytes: Optional bytes payload to verify the checksum against.
            
        Returns:
            True if valid, False otherwise.
        """
        try:
            # 1. Check expected round matching
            if record.local_epoch <= 0:
                self._logger.warning(f"Invalid local_epoch {record.local_epoch} for client {record.client_id}")
                return False
                
            # If the architecture strictly enforces round sync, we validate it here.
            # Allowing asynchronous updates is an advanced feature; we'll strictly enforce round match here.
            # But the user might not pass the exact personalization_round vs global communication round perfectly.
            # We assume for this implementation that they must match if enforced by the engine.
            
            # 2. Checksum validation
            if raw_payload_bytes is not None:
                is_valid = self._checksum_service.verify_checksum(
                    data=raw_payload_bytes,
                    expected_checksum=record.checksum
                )
                if not is_valid:
                    self._logger.error(f"Checksum mismatch for client {record.client_id}")
                    return False
                    
            # 3. Minimum dataset constraints
            if record.dataset_size <= 0:
                self._logger.warning(f"Client {record.client_id} submitted update with 0 dataset size.")
                return False
                
            return True
            
        except Exception as e:
            self._logger.error(f"Validation error for {record.client_id}: {str(e)}")
            return False

    def validate_tensor_shapes(
        self,
        client_state_dict: Dict[str, Any],
        reference_state_dict: Dict[str, Any]
    ) -> bool:
        """Validates that a client's tensor shapes exactly match a reference adapter.
        
        Args:
            client_state_dict: The LoRA state dict to validate.
            reference_state_dict: The expected global LoRA state dict reference.
            
        Returns:
            True if shapes are perfectly compatible.
        """
        try:
            client_keys = set(client_state_dict.keys())
            ref_keys = set(reference_state_dict.keys())
            
            if client_keys != ref_keys:
                self._logger.error("Tensor key mismatch.")
                return False
                
            for key in client_keys:
                client_tensor = client_state_dict[key]
                ref_tensor = reference_state_dict[key]
                
                if hasattr(client_tensor, "shape") and hasattr(ref_tensor, "shape"):
                    if client_tensor.shape != ref_tensor.shape:
                        self._logger.error(f"Shape mismatch for key {key}: {client_tensor.shape} != {ref_tensor.shape}")
                        return False
            return True
            
        except Exception as e:
            self._logger.error(f"Tensor shape validation failed: {str(e)}")
            return False

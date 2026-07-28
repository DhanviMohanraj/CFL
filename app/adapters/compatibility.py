"""DriftAdapt Merge Compatibility Checker.

Author: DriftAdapt Contributors
Purpose: Cross-references metadata to ensure adapters are eligible for merging.
"""

from typing import List

from app.adapters.merge_exceptions import IncompatibleAdapters
from app.adapters.version_metadata import AdapterVersionMetadata
from app.core.logging.logger_factory import LoggerFactory


class CompatibilityChecker:
    """Ensures input adapters share compatible architectural properties."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("CompatibilityChecker")
        
    def verify_compatibility(self, metadata_list: List[AdapterVersionMetadata]) -> None:
        """Verifies that a list of adapter versions are compatible for merging.
        
        Args:
            metadata_list: List of version metadata entries.
            
        Raises:
            IncompatibleAdapters: If any configuration or parameter count mismatches.
        """
        if not metadata_list:
            return
            
        base = metadata_list[0]
        
        for m in metadata_list[1:]:
            if m.parameter_count != base.parameter_count:
                raise IncompatibleAdapters(
                    f"Parameter count mismatch: {m.version_id} ({m.parameter_count}) != {base.version_id} ({base.parameter_count})"
                )
            if m.serialization_format != base.serialization_format:
                raise IncompatibleAdapters(
                    f"Serialization format mismatch: {m.version_id} ({m.serialization_format}) != {base.version_id} ({base.serialization_format})"
                )
                
        self._logger.debug("Compatibility check passed for parameter counts and formats.")

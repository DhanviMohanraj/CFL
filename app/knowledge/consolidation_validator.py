"""DriftAdapt Knowledge Consolidation Validator.

Author: DriftAdapt Contributors
"""

from app.knowledge.consolidation_schema import ConsolidationRecord
from app.knowledge.consolidation_exceptions import KnowledgeConsolidationError


class ConsolidationValidator:
    """Validates inputs for knowledge consolidation."""
    
    def validate(self, round_id: int, adapter_path: str) -> None:
        if round_id < 0:
            raise KnowledgeConsolidationError("Round ID must be non-negative.")
        if not adapter_path:
            raise KnowledgeConsolidationError("Adapter path must be provided.")

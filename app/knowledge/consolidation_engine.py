"""DriftAdapt Knowledge Consolidation Engine.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any
from app.core.metrics.metrics_bus import MetricsBus
from app.knowledge.consolidation_schema import ConsolidationRecord
from app.knowledge.consolidation_exceptions import KnowledgeConsolidationError
from app.knowledge.consolidation_logger import ConsolidationLogger
from app.knowledge.consolidation_metrics import ConsolidationMetrics
from app.knowledge.consolidation_registry import ConsolidationRegistry
from app.knowledge.consolidation_history import ConsolidationHistory
from app.knowledge.consolidation_validator import ConsolidationValidator
from app.knowledge.consolidation_manager import ConsolidationManager


class KnowledgeConsolidationEngine:
    """Core engine for knowledge consolidation and catastrophic forgetting prevention."""
    
    def __init__(self, config: Dict[str, Any], metrics_bus: MetricsBus) -> None:
        self.config = config
        self.metrics = ConsolidationMetrics(metrics_bus)
        self.logger = ConsolidationLogger()
        self.registry = ConsolidationRegistry()
        self.history = ConsolidationHistory()
        self.validator = ConsolidationValidator()
        self.manager = ConsolidationManager(self.registry)
        self._initialized = False
        
    def initialize(self) -> None:
        self._initialized = True
        self.logger.info("KnowledgeConsolidationEngine initialized")
        
    def consolidate(self, round_id: int, adaptive_global_adapter_path: str) -> ConsolidationRecord:
        """Consolidates the adaptive global adapter."""
        if not self._initialized:
            raise KnowledgeConsolidationError("Engine not initialized.")
            
        self.logger.info(f"Consolidating knowledge for round {round_id}")
        self.metrics.publish_event("knowledge.consolidation.started")
        
        try:
            self.validator.validate(round_id, adaptive_global_adapter_path)
            
            # Placeholder for complex logic (merging, privacy, memory)
            strategy = self.config.get("knowledge", {}).get("consolidation_strategy", "simple")
            
            record = ConsolidationRecord(
                round_id=round_id,
                adaptive_global_adapter_path=adaptive_global_adapter_path,
                strategy_name=strategy,
                consolidated_adapter_path=f"consolidated_{round_id}.pt"
            )
            
            self.manager.track_consolidation(record)
            self.history.record_consolidation(record)
            
            self.metrics.publish_event("knowledge.consolidation.completed")
            self.logger.info(f"Successfully consolidated knowledge: {record.consolidation_id}")
            
            return record
            
        except Exception as e:
            self.logger.error(f"Failed to consolidate knowledge: {str(e)}")
            raise KnowledgeConsolidationError(f"Knowledge consolidation failed: {str(e)}") from e

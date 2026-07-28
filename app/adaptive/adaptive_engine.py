"""DriftAdapt Adaptive Engine.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any
from app.core.metrics.metrics_bus import MetricsBus
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptive.adaptive_schema import AdaptiveRecord
from app.adaptive.adaptive_exceptions import AdaptiveInitializationError, AdaptiveExecutionError
from app.adaptive.adaptive_logger import AdaptiveLogger
from app.adaptive.adaptive_metrics import AdaptiveMetrics
from app.adaptive.adaptive_registry import AdaptiveRegistry
from app.adaptive.adaptive_history import AdaptiveHistory
from app.adaptive.adaptive_validator import AdaptiveValidator
from app.adaptive.adaptive_manager import AdaptiveManager
from app.adaptive.utilities.strategy_selector import StrategySelector


class AdaptiveFederationEngine:
    """Core engine for adaptive federated execution."""
    
    def __init__(self, config: Dict[str, Any], metrics_bus: MetricsBus, strategy_selector: StrategySelector) -> None:
        self.config = config
        self.metrics = AdaptiveMetrics(metrics_bus)
        self.logger = AdaptiveLogger()
        self.registry = AdaptiveRegistry()
        self.history = AdaptiveHistory()
        self.validator = AdaptiveValidator()
        self.manager = AdaptiveManager(self.registry)
        self.strategy_selector = strategy_selector
        self._initialized = False
        
    def initialize(self) -> None:
        self._initialized = True
        self.logger.info("AdaptiveFederationEngine initialized")
        
    def execute(self, decision: AdaptationDecision) -> AdaptiveRecord:
        """Executes an adaptation decision."""
        if not self._initialized:
            raise AdaptiveInitializationError("Engine not initialized.")
            
        self.logger.info(f"Executing adaptation decision: {decision.decision_id}")
        self.metrics.publish_event("adaptive.started")
        
        try:
            self.validator.validate_decision(decision)
            
            strategy = self.strategy_selector.select(decision, self.config)
            self.metrics.publish_value("adaptive.strategy", strategy.__class__.__name__)
            
            # Aggregate via strategy
            record = strategy.execute(decision, self.config)
            
            self.manager.track_execution(record)
            
            if self.config.get("effectiveness_tracking", True):
                self.history.record_execution(record)
                
            self.metrics.publish_event("adaptive.completed")
            self.logger.info(f"Successfully executed adaptation: {record.adaptation_id}")
            
            return record
            
        except Exception as e:
            self.metrics.publish_event("adaptive.failed")
            self.logger.error(f"Failed to execute adaptation: {str(e)}")
            raise AdaptiveExecutionError(f"Adaptive execution failed: {str(e)}") from e

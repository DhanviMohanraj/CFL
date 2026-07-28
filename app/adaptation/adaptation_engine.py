"""DriftAdapt Adaptation Engine.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any, List
from app.core.metrics.metrics_bus import MetricsBus
from app.drift.drift_schema import DriftReport

from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptation.decision_engine import DecisionEngine
from app.adaptation.adaptation_manager import AdaptationManager
from app.adaptation.decision_registry import DecisionRegistry
from app.adaptation.decision_history import DecisionHistory
from app.adaptation.adaptation_scheduler import AdaptationScheduler
from app.adaptation.adaptation_validator import AdaptationValidator
from app.adaptation.adaptation_metrics import AdaptationMetrics
from app.adaptation.adaptation_logger import AdaptationLogger
from app.adaptation.policy_factory import PolicyFactory
from app.adaptation.adaptation_exceptions import AdaptationInitializationError, AdaptationError


class AdaptationEngine:
    """Core engine for continual adaptation decisions."""
    
    def __init__(self, config: Dict[str, Any], metrics_bus: MetricsBus, policy_factory: PolicyFactory) -> None:
        self.config = config
        
        self.registry = DecisionRegistry()
        self.manager = AdaptationManager(self.registry)
        self.history = DecisionHistory()
        self.validator = AdaptationValidator()
        self.scheduler = AdaptationScheduler()
        
        self.policy_factory = policy_factory
        self.decision_engine = DecisionEngine(self.policy_factory)
        
        self.metrics = AdaptationMetrics(metrics_bus)
        self.logger = AdaptationLogger()
        self._initialized = False
        
    def initialize(self) -> None:
        """Initializes the adaptation engine."""
        self._initialized = True
        self.logger.info("AdaptationEngine initialized")
        
    def decide(self, drift_reports: List[DriftReport]) -> AdaptationDecision:
        """Analyzes drift reports and generates an adaptation decision."""
        if not self._initialized:
            raise AdaptationInitializationError("AdaptationEngine must be initialized before deciding.")
            
        self.logger.info(f"Analyzing {len(drift_reports)} drift reports for adaptation")
        
        try:
            self.validator.validate_reports(drift_reports)
            
            best_policy, confidence = self.decision_engine.evaluate(drift_reports, self.config)
            
            decision = best_policy.generate_decision(drift_reports, confidence, self.config)
            
            decision.urgency = self.scheduler.schedule(decision, self.config)
            
            self.manager.track_decision(decision)
            
            if self.config.get("history_enabled", True):
                self.history.record_decision(decision)
                
            self.metrics.publish_event("adaptation.decision.generated")
            self.metrics.publish_value("adaptation.confidence", confidence)
            self.metrics.publish_value("adaptation.clinic.count", len(decision.affected_clinics))
            
            # Policy specific metrics
            p_name = decision.policy_name.lower()
            if "global" in p_name:
                self.metrics.publish_event("adaptation.global")
            elif "local" in p_name:
                self.metrics.publish_event("adaptation.local")
            elif "emergency" in p_name:
                self.metrics.publish_event("adaptation.emergency")
                
            self.logger.info(f"Adaptation decision generated: {decision.policy_name} with priority {decision.priority}")
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Failed to generate adaptation decision: {str(e)}")
            raise AdaptationError(f"Decision failed: {str(e)}") from e

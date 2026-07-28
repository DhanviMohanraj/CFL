"""DriftAdapt Drift Engine.

Author: DriftAdapt Contributors
"""

import time
from typing import Dict, Any, List
import pandas as pd

from app.core.metrics.metrics_bus import MetricsBus
from app.drift.drift_schema import DriftReport, FeatureDriftScore
from app.drift.drift_manager import DriftManager
from app.drift.drift_registry import DriftRegistry
from app.drift.drift_history import DriftHistory
from app.drift.drift_reporter import DriftReporter
from app.drift.drift_validator import DriftValidator
from app.drift.drift_analyzer import DriftAnalyzer
from app.drift.drift_metrics import DriftMetrics
from app.drift.drift_logger import DriftLogger
from app.drift.drift_exceptions import DriftInitializationError, DriftError


class DriftEngine:
    """Core engine for detecting healthcare data drift."""
    
    def __init__(self, config: Dict[str, Any], metrics_bus: MetricsBus, detectors: List[Any]) -> None:
        self.config = config
        
        self.registry = DriftRegistry()
        self.manager = DriftManager(self.registry)
        self.history = DriftHistory()
        self.reporter = DriftReporter()
        self.validator = DriftValidator()
        self.analyzer = DriftAnalyzer(detectors)
        
        self.metrics = DriftMetrics(metrics_bus)
        self.logger = DriftLogger()
        self._initialized = False
        
    def initialize(self) -> None:
        """Initializes the drift engine."""
        self._initialized = True
        self.logger.info("DriftEngine initialized")
        
    def detect(self, clinic_id: str, month: int, baseline_month: int, reference_df: pd.DataFrame, current_df: pd.DataFrame) -> DriftReport:
        """Runs end-to-end drift detection."""
        if not self._initialized:
            raise DriftInitializationError("DriftEngine must be initialized before detection.")
            
        start_time = time.time()
        self.logger.info(f"Starting drift detection for clinic {clinic_id}, month {month} vs {baseline_month}")
        
        try:
            self.validator.validate_datasets(reference_df, current_df)
            
            feature_scores = self.analyzer.analyze(reference_df, current_df, self.config)
            
            drifting_features = [s for s in feature_scores if s.is_drift]
            drift_detected = len(drifting_features) > 0
            
            if drift_detected:
                if len(drifting_features) > 5:
                    severity = "SIGNIFICANT"
                else:
                    severity = "MODERATE"
                drift_type = "COVARIATE"
                self.metrics.publish_event("drift.detected", {"clinic": clinic_id, "month": str(month)})
            else:
                severity = "NONE"
                drift_type = "NONE"
                self.metrics.publish_event("drift.none", {"clinic": clinic_id, "month": str(month)})
                
            report = DriftReport(
                clinic_id=clinic_id,
                month=month,
                baseline_month=baseline_month,
                feature_scores=feature_scores,
                drift_detected=drift_detected,
                drift_type=drift_type,
                severity=severity,
                metrics={"duration": time.time() - start_time}
            )
            
            self.manager.track_report(report)
            
            if self.config.get("store_history", True):
                self.history.record_report(report)
                
            self.metrics.publish_value("drift.feature.count", len(feature_scores), {"clinic": clinic_id})
            self.metrics.publish_value("drift.analysis.time", time.time() - start_time)
            
            self.logger.info(f"Drift detection completed for {clinic_id}. Detected: {drift_detected}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Drift detection failed for {clinic_id}: {str(e)}")
            raise DriftError(f"Detection failed: {str(e)}") from e
            
    def report(self, clinic_id: str, month: int) -> str:
        """Generates a JSON report for a given detection."""
        report = self.registry.lookup(clinic_id, month)
        if not report:
            return "{}"
        return self.reporter.generate_json(report)

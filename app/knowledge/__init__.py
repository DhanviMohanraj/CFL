"""DriftAdapt Knowledge Consolidation Module.

Author: DriftAdapt Contributors
"""

from app.knowledge.consolidation_exceptions import (
    KnowledgeConsolidationError,
    PrototypeUpdateError,
    ForgettingDetectionError,
    DifferentialPrivacyError,
    PrivacyBudgetExceededError,
    SVDConsolidationError,
    PseudoinverseError,
    StatisticsUpdateError,
    RegistryError
)
from app.knowledge.consolidation_schema import ConsolidationRecord
from app.knowledge.consolidation_registry import ConsolidationRegistry
from app.knowledge.consolidation_logger import ConsolidationLogger
from app.knowledge.consolidation_metrics import ConsolidationMetrics
from app.knowledge.consolidation_history import ConsolidationHistory
from app.knowledge.consolidation_validator import ConsolidationValidator
from app.knowledge.consolidation_manager import ConsolidationManager
from app.knowledge.consolidation_engine import KnowledgeConsolidationEngine

__all__ = [
    "KnowledgeConsolidationError",
    "PrototypeUpdateError",
    "ForgettingDetectionError",
    "DifferentialPrivacyError",
    "PrivacyBudgetExceededError",
    "SVDConsolidationError",
    "PseudoinverseError",
    "StatisticsUpdateError",
    "RegistryError",
    "ConsolidationRecord",
    "ConsolidationRegistry",
    "ConsolidationLogger",
    "ConsolidationMetrics",
    "ConsolidationHistory",
    "ConsolidationValidator",
    "ConsolidationManager",
    "KnowledgeConsolidationEngine"
]

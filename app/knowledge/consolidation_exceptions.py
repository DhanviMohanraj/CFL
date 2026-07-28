"""DriftAdapt Knowledge Consolidation Exceptions.

Author: DriftAdapt Contributors
"""


class KnowledgeConsolidationError(Exception):
    """Base exception for all knowledge consolidation errors."""
    pass


class PrototypeUpdateError(KnowledgeConsolidationError):
    """Raised when updating the prototype bank fails."""
    pass


class ForgettingDetectionError(KnowledgeConsolidationError):
    """Raised when forgetting detection fails."""
    pass


class DifferentialPrivacyError(KnowledgeConsolidationError):
    """Raised when applying differential privacy fails."""
    pass


class PrivacyBudgetExceededError(DifferentialPrivacyError):
    """Raised when the privacy budget is exceeded."""
    pass


class SVDConsolidationError(KnowledgeConsolidationError):
    """Raised when SVD consolidation fails."""
    pass


class PseudoinverseError(KnowledgeConsolidationError):
    """Raised when pseudoinverse calculation fails."""
    pass


class StatisticsUpdateError(KnowledgeConsolidationError):
    """Raised when online statistics update fails."""
    pass


class RegistryError(KnowledgeConsolidationError):
    """Raised when registry operations fail."""
    pass

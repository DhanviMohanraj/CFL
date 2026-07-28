"""DriftAdapt Aggregation Exceptions.

Author: DriftAdapt Contributors
"""


class AggregationError(Exception):
    """Base exception for all aggregation errors."""
    pass


class AggregationInitializationError(AggregationError):
    """Raised when aggregation initialization fails."""
    pass


class AlgorithmSelectionError(AggregationError):
    """Raised when an invalid aggregation algorithm is requested."""
    pass


class AdapterCompatibilityError(AggregationError):
    """Raised when adapters are incompatible for merging."""
    pass


class TensorShapeError(AggregationError):
    """Raised when tensor shapes do not match."""
    pass


class WeightedAggregationError(AggregationError):
    """Raised when weights are invalid for weighted aggregation."""
    pass


class FedProxExecutionError(AggregationError):
    """Raised when FedProx aggregation fails."""
    pass


class ValidationFailure(AggregationError):
    """Raised when adapter or tensor validation fails."""
    pass


class AggregationExportError(AggregationError):
    """Raised when exporting the global adapter fails."""
    pass


class RegistryError(AggregationError):
    """Raised when registry operations fail."""
    pass

"""DriftAdapt Merge Engine Exceptions.

Author: DriftAdapt Contributors
Purpose: Defines custom exceptions for the baseline merge engine.
"""


class MergeFailed(Exception):
    """Base exception for all merge failures."""
    pass


class IncompatibleAdapters(MergeFailed):
    """Raised when adapters cannot be merged due to differing metadata or configurations."""
    pass


class InvalidMergeStrategy(MergeFailed):
    """Raised when an unknown or unsupported strategy is requested."""
    pass


class TensorShapeMismatch(MergeFailed):
    """Raised when tensors across adapters do not match in shape."""
    pass


class ChecksumValidationFailed(MergeFailed):
    """Raised when an adapter payload fails checksum validation before merging."""
    pass


class DuplicateAdapterError(MergeFailed):
    """Raised when duplicate adapter IDs are supplied to the merge engine."""
    pass


class EmptyMergeInput(MergeFailed):
    """Raised when zero or one adapter is provided for merging."""
    pass

"""DriftAdapt Merging Module.

Author: DriftAdapt Contributors
"""

from app.knowledge.merging.svd_merger import SVDMerger
from app.knowledge.merging.pseudoinverse_merger import PseudoinverseMerger
from app.knowledge.merging.adapter_reconstructor import AdapterReconstructor
from app.knowledge.merging.consolidation_strategy import (
    BaseConsolidationStrategy,
    SimpleConsolidation,
    SVDConsolidation,
    HybridConsolidation
)

__all__ = [
    "SVDMerger",
    "PseudoinverseMerger",
    "AdapterReconstructor",
    "BaseConsolidationStrategy",
    "SimpleConsolidation",
    "SVDConsolidation",
    "HybridConsolidation"
]

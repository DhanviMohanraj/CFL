"""DriftAdapt Algorithms Module.

Author: DriftAdapt Contributors
"""

from app.aggregation.algorithms.base_algorithm import BaseAlgorithm
from app.aggregation.algorithms.fedavg import FedAvg
from app.aggregation.algorithms.weighted_fedavg import WeightedFedAvg
from app.aggregation.algorithms.fedprox import FedProx
from app.aggregation.algorithms.static_fedlora import StaticFedLoRA
from app.aggregation.algorithms.identity import IdentityAggregation

__all__ = [
    "BaseAlgorithm",
    "FedAvg",
    "WeightedFedAvg",
    "FedProx",
    "StaticFedLoRA",
    "IdentityAggregation",
]

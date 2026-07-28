"""DriftAdapt Aggregation Factory.

Author: DriftAdapt Contributors
"""

from app.aggregation.algorithms.base_algorithm import BaseAlgorithm
from app.aggregation.algorithms.fedavg import FedAvg
from app.aggregation.algorithms.weighted_fedavg import WeightedFedAvg
from app.aggregation.algorithms.fedprox import FedProx
from app.aggregation.algorithms.static_fedlora import StaticFedLoRA
from app.aggregation.algorithms.identity import IdentityAggregation
from app.aggregation.aggregation_exceptions import AlgorithmSelectionError


class AggregationFactory:
    """Factory for creating aggregation algorithms."""
    
    @staticmethod
    def get_algorithm(name: str) -> BaseAlgorithm:
        name = name.lower()
        if name == "fedavg":
            return FedAvg()
        elif name == "weighted_fedavg":
            return WeightedFedAvg()
        elif name == "fedprox":
            return FedProx()
        elif name == "static_fedlora":
            return StaticFedLoRA()
        elif name == "identity":
            return IdentityAggregation()
        else:
            raise AlgorithmSelectionError(f"Unsupported aggregation algorithm: {name}")

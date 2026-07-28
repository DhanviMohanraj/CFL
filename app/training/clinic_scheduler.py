"""DriftAdapt Clinic Scheduler.

Author: DriftAdapt Contributors
"""

import random
from typing import List
from abc import ABC, abstractmethod


class ClinicSelectionStrategy(ABC):
    """Base strategy for selecting participating clinics."""
    
    @abstractmethod
    def select(self, available_clinics: List[str], **kwargs) -> List[str]:
        pass


class AllClinicsStrategy(ClinicSelectionStrategy):
    """Selects all available clinics."""
    
    def select(self, available_clinics: List[str], **kwargs) -> List[str]:
        return list(available_clinics)


class RandomSubsetStrategy(ClinicSelectionStrategy):
    """Selects a random subset of clinics."""
    
    def select(self, available_clinics: List[str], **kwargs) -> List[str]:
        subset_size = kwargs.get("subset_size", len(available_clinics))
        if subset_size > len(available_clinics):
            subset_size = len(available_clinics)
        return random.sample(available_clinics, subset_size)


class PercentageParticipationStrategy(ClinicSelectionStrategy):
    """Selects a percentage of available clinics."""
    
    def select(self, available_clinics: List[str], **kwargs) -> List[str]:
        percentage = kwargs.get("percentage", 1.0)
        subset_size = max(1, int(len(available_clinics) * percentage))
        return random.sample(available_clinics, subset_size)


class ClinicScheduler:
    """Manages the selection of clinics for a training round."""
    
    def __init__(self, strategy: ClinicSelectionStrategy) -> None:
        self._strategy = strategy
        
    def select_clinics(self, available_clinics: List[str], **kwargs) -> List[str]:
        """Selects clinics using the provided strategy."""
        return self._strategy.select(available_clinics, **kwargs)

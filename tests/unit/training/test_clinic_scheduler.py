"""Tests for Clinic Scheduler.

Author: DriftAdapt Contributors
"""

from app.training.clinic_scheduler import (
    ClinicScheduler,
    AllClinicsStrategy,
    RandomSubsetStrategy,
    PercentageParticipationStrategy,
)


def test_all_clinics_strategy():
    strategy = AllClinicsStrategy()
    clinics = ["c1", "c2", "c3"]
    assert len(strategy.select(clinics)) == 3

def test_random_subset_strategy():
    strategy = RandomSubsetStrategy()
    clinics = ["c1", "c2", "c3"]
    assert len(strategy.select(clinics, subset_size=2)) == 2

def test_percentage_strategy():
    strategy = PercentageParticipationStrategy()
    clinics = ["c1", "c2", "c3", "c4"]
    assert len(strategy.select(clinics, percentage=0.5)) == 2
    assert len(strategy.select(clinics, percentage=1.0)) == 4

"""Tests for Reproducibility.

Author: DriftAdapt Contributors
"""

from app.evaluation.reproducibility.experiment_manifest import ExperimentManifest


def test_experiment_manifest():
    manifest = ExperimentManifest()
    assert manifest is not None

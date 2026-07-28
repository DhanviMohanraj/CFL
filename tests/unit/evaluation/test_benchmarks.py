"""Tests for Benchmarks.

Author: DriftAdapt Contributors
"""

from app.evaluation.benchmarks.medmcqa import MedMCQABenchmark


def test_medmcqa_benchmark():
    benchmark = MedMCQABenchmark()
    assert benchmark is not None

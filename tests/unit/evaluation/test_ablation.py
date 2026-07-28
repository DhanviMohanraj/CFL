"""Tests for Ablation.

Author: DriftAdapt Contributors
"""

from app.evaluation.ablation.ablation_manager import AblationManager


def test_ablation_manager():
    manager = AblationManager()
    assert manager is not None

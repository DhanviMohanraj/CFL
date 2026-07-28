"""Tests for Drift Utilities.

Author: DriftAdapt Contributors
"""

import pandas as pd
import numpy as np
from app.drift.utilities.distribution_builder import DistributionBuilder
from app.drift.utilities.feature_statistics import FeatureStatistics
from app.drift.utilities.histogram_builder import HistogramBuilder
from app.drift.utilities.threshold_manager import ThresholdManager


def test_distribution_builder():
    ref = pd.Series([1, 2, 3, 4, 5])
    cur = pd.Series([1, 2, 3, 4, 5])
    
    p, q = DistributionBuilder.build_distributions(ref, cur)
    assert len(p) == 10
    assert len(q) == 10
    
    ref_cat = pd.Series(["A", "B", "A"])
    cur_cat = pd.Series(["A", "B", "B"])
    p, q = DistributionBuilder.build_distributions(ref_cat, cur_cat)
    assert len(p) == 2


def test_feature_statistics():
    data = pd.Series([1, 2, 3, np.nan])
    stats = FeatureStatistics.compute(data)
    assert stats["missing_count"] == 1
    assert stats["mean"] == 2.0


def test_histogram_builder():
    data = pd.Series([1, 2, 3, 4, 5])
    counts, bins = HistogramBuilder.build(data, bins=5)
    assert len(counts) == 5
    assert len(bins) == 6


def test_threshold_manager():
    config = {"psi_threshold": 0.3}
    manager = ThresholdManager(config)
    assert manager.get_threshold("PSI") == 0.3
    assert manager.get_threshold("KL") == 0.15 # default

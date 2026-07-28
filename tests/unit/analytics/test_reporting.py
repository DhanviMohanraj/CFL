"""Tests for Reporting.

Author: DriftAdapt Contributors
"""

from app.analytics.reporting.report_generator import ReportGenerator


def test_report_generator():
    generator = ReportGenerator()
    assert generator is not None

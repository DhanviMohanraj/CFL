"""Tests for Exporters.

Author: DriftAdapt Contributors
"""

from app.analytics.exporters.json_exporter import JSONExporter


def test_json_exporter():
    exporter = JSONExporter()
    assert exporter is not None

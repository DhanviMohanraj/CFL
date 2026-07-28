"""Tests for Publication.

Author: DriftAdapt Contributors
"""

from app.evaluation.publication.latex_generator import LaTeXGenerator


def test_latex_generator():
    generator = LaTeXGenerator()
    assert generator is not None

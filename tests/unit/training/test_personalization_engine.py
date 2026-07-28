"""Tests for Personalization Engine.

Author: DriftAdapt Contributors
"""

from app.training.personalization_engine import PersonalizationEngine


def test_personalization_engine():
    engine = PersonalizationEngine({})
    model = engine.prepare_model()
    
    assert hasattr(model, "lora_layer")

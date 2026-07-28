"""DriftAdapt Adaptive Validator.

Author: DriftAdapt Contributors
"""

from typing import List, Dict, Any
from app.adaptation.adaptation_schema import AdaptationDecision
from app.adaptive.adaptive_exceptions import ValidationError


class AdaptiveValidator:
    """Validates inputs for adaptive execution."""
    
    def validate_decision(self, decision: AdaptationDecision) -> None:
        if not decision.adaptation_required:
            raise ValidationError("Adaptation is not required according to the decision.")
        if not decision.affected_clinics:
            raise ValidationError("No affected clinics provided in the adaptation decision.")

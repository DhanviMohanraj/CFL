"""Prompt Metadata Schema.

Author: DriftAdapt Contributors
Purpose: Captures analytical metadata about the incoming prompts.
"""

from pydantic import BaseModel, Field


class PromptMetadata(BaseModel):
    """Metadata inferred or calculated from the input prompt."""
    
    language: str = Field(default="unknown", description="Detected ISO language code (e.g., 'en', 'fr')")
    prompt_length: int = Field(default=0, description="Raw character length of the prompt")
    detected_domain: str = Field(default="general", description="Thematic domain classification (e.g., 'healthcare', 'finance')")
    estimated_complexity: float = Field(default=0.0, description="Heuristic complexity score (0.0 to 1.0)")
    preprocessing_time: float = Field(default=0.0, description="Time taken to parse and format the prompt in seconds")

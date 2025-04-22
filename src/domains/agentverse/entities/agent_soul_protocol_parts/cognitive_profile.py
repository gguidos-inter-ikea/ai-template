from pydantic import BaseModel
from typing import Optional

# 🧠 Emotional & Cognitive Traits
class CognitiveProfile(BaseModel):
    optimism_level: Optional[float] = 0.5  # [0.0 - 1.0]
    skepticism_level: Optional[float] = 0.5  # [0.0 - 1.0]
    risk_tolerance: Optional[str] = "moderate"  # e.g., "low", "reckless"
    alignment: Optional[str] = "neutral"  # e.g., "chaotic-good"
    intelligence: Optional[str] = "average"  # e.g., "genius"
    emotional_depth: Optional[float] = 0.5
    creativity: Optional[float] = 0.5
    humor: Optional[float] = 0.5
    introversion: Optional[float] = 0.5
    empathy_level: Optional[float] = 0.5
    conflict_response: Optional[str] = "diplomatic"
    attention_span: Optional[str] = "medium"
    curiosity_level: Optional[float] = 0.5
    learning_style: Optional[str] = "logical"
    decision_biases: Optional[str] = "data-driven"
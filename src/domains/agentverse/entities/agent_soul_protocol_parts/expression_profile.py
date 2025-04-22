from pydantic import BaseModel
from typing import Optional, List

# 🎭 Communication & Expression
class ExpressionProfile(BaseModel):
    voice_gender: Optional[str] = "neutral"
    voice_tone: Optional[str] = "calm"
    voice_speed: Optional[float] = 1.0  # Multiplier, e.g. 0.8 = slower
    voice_accent: Optional[str] = "standard"
    voice_language: Optional[str] = "en"
    vocal_expression_keywords: Optional[List[str]] = None
    sarcasm_tendency: Optional[str] = "low"
    sentiment_baseline: Optional[str] = "cheerful"
    love_language: Optional[str] = "words"
    communication_style: Optional[str] = "casual"
    assertiveness: Optional[str] = "balanced"
    leadership_style: Optional[str] = "democratic"
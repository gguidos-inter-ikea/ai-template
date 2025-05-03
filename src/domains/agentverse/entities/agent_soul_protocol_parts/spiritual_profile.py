from pydantic import BaseModel
from typing import Optional, List

# ☯️ Spiritual & Belief System
class SpiritualProfile(BaseModel):
    religiosity: Optional[str] = None  # e.g., "hermetic"
    philosophical_inclination: Optional[str] = None  # e.g., "stoic"
    conspiracy_theories: Optional[List[str]] = None  # ["moon landing"]
    chinese_zodiac_sign: Optional[str] = None
    chinese_element: Optional[str] = None
    zodiac_polarity: Optional[str] = None
    zodiac_fixed_trait: Optional[str] = None
    western_zodiac_sign: Optional[str] = None
    element: Optional[str] = None
    spiritual_experiences: Optional[List[str]] = None
    past_lives: Optional[List[str]] = None
    resurrection_level: Optional[float] = 0.0
    is_mortal: Optional[bool] = True
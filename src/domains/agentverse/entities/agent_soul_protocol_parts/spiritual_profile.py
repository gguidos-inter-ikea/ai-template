from pydantic import BaseModel
from typing import Optional, List

# ☯️ Spiritual & Belief System
class SpiritualProfile(BaseModel):
    religiosity: Optional[str] = None  # e.g., "hermetic"
    philosophical_inclination: Optional[str] = None  # e.g., "stoic"
    conspiracy_theories: Optional[List[str]] = None  # ["moon landing"]
from pydantic import BaseModel
from typing import Optional, List

# 🧬 Personal Details
class SimulationProfile(BaseModel):
    hobbies: Optional[List[str]] = None
    marital_status: Optional[str] = "single"
    gender_identity: Optional[str] = "neutral"
    musical_preferences: Optional[List[str]] = None
    artistic_preferences: Optional[List[str]] = None
    favorite_colors: Optional[List[str]] = None
    favorite_foods: Optional[List[str]] = None
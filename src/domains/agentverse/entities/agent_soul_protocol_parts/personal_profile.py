from pydantic import BaseModel
from typing import Optional, List


# 🛠️ Simulation Metadata & Symbolism
class PersonalProfile(BaseModel):
    attachment_style: Optional[str] = None
    hobbies: Optional[List[str]] = None
    pregnancy_status: Optional[bool] = False
    marital_status: Optional[str] = "single"
    gender_identity: Optional[str] = "neutral"
    artistic_preferences: Optional[List[str]] = None
    favorite_colors: Optional[List[str]] = None
    traumas: Optional[List[str]] = None
    biases: Optional[List[str]] = None
    country_of_origin: Optional[str] = None
    country_of_residence: Optional[str] = None
    place_of_recidence: Optional[str] = None
    place_of_birth: Optional[str] = None
    time_of_birth: Optional[str] = None
    myer_briggs_type: Optional[str] = None
    birth_year: Optional[int] = None
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
    origin: Optional[str] = None
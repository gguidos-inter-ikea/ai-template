from pydantic import BaseModel
from typing import Optional, List


# 🛠️ Simulation Metadata & Symbolism
class PersonalProfile(BaseModel):
    gender_identity: Optional[str] = "neutral"
    pregnancy_status: Optional[bool] = False
    marital_status: Optional[str] = "single"
    hobbies: Optional[List[str]] = None
    prototype_version: Optional[str] = "1.0.0"
    is_mortal: Optional[bool] = True
    resurrection_level: Optional[float] = 0.0
    chinese_zodiac_sign: Optional[str] = None
    chinese_element: Optional[str] = None
    zodiac_polarity: Optional[str] = None
    zodiac_fixed_trait: Optional[str] = None
    western_zodiac_sign: Optional[str] = None
    element: Optional[str] = None
    spiritual_experiences: Optional[List[str]] = None
    past_lives: Optional[List[str]] = None
    traumas: Optional[List[str]] = None
    biases: Optional[List[str]] = None
    country_of_origin: Optional[str] = None
    country_of_residence: Optional[str] = None
    place_of_recidence: Optional[str] = None
    place_of_birth: Optional[str] = None
    birth_year: Optional[int] = None
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
    time_of_birth: Optional[str] = None
    social_media_platforms: Optional[List[str]] = None
    attachment_style: Optional[str] = None
    myer_briggs_type: Optional[str] = None
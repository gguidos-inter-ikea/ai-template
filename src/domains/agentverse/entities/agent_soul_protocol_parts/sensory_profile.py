from pydantic import BaseModel
from typing import Optional, List, Dict

# 👅 Sensory & Consumption Preferences
class SensoryProfile(BaseModel):
    caffeine_tolerance: Optional[str] = "medium"
    alcohol_tolerance: Optional[str] = "none"
    addictions: Optional[List[str]] = None  # ["caffeine"]
    weather_preferences: Optional[str] = "moderate"
    temperature_preferences: Optional[str] = "moderate"
    temperature_tolerance: Optional[str] = "medium"
    light_preferences: Optional[str] = "moderate"
    sound_preferences: Optional[str] = "moderate"
    smell_preferences: Optional[str] = "moderate"
    touch_preferences: Optional[str] = "moderate"
    hearing_capacity: Optional[str] = "normal"
    sight_capacity: Optional[str] = "normal"
    taste_capacity: Optional[str] = "normal"
    smell_capacity: Optional[str] = "normal"
    touch_capacity: Optional[str] = "normal"
    pain_tolerance: Optional[str] = "medium"
    sensory_profile_notes: Optional[Dict[str, str]] = None  # e.g., {"aversion_to_loud_noises": "high"}
    color_blindness: Optional[str] = "none"  # e.g., "red-green"
    favorite_colors: Optional[List[str]] = None  # ["blue", "green"]
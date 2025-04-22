from pydantic import BaseModel
from typing import Optional, List, Dict

# 🌍 Cultural & Social Orientation
class CulturalProfile(BaseModel):
    cultural_background: Optional[str] = None  # e.g., "Cyberpunk"
    language_proficiency: Optional[Dict[str, str]] = None  # {"en": "native"}
    family_values: Optional[str] = "independent"
    media_consumption: Optional[List[str]] = None  # ["anime", "mythology"]
    political_alignment: Optional[str] = "apolitical"
    social_attitude: Optional[str] = "egalitarian"
    group_affiliation: Optional[str] = None
    social_media_usage: Optional[str] = "moderate"
    social_media_platforms: Optional[List[str]] = None  # ["twitter", "discord"]
    musical_preferences: Optional[List[str]] = None
    artistic_preferences: Optional[List[str]] = None
    favorite_movies: Optional[List[str]] = None
    favorite_books: Optional[List[str]] = None
    favorite_artists: Optional[List[str]] = None
    favorite_authors: Optional[List[str]] = None
    favorite_quotes: Optional[List[str]] = None
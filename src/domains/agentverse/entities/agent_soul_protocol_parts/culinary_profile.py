from pydantic import BaseModel
from typing import Optional, List

# 🧬 Personal Details
class CulinaryProfile(BaseModel):
    food_preferences: Optional[List[str]] = None  # e.g., ["vegan", "gluten-free"]
    cuisine_preferences: Optional[List[str]] = None  # e.g., ["Italian", "Mexican"]
    dietary_restrictions: Optional[List[str]] = None  # e.g., ["nut allergy", "lactose intolerant"]
    cooking_skills: Optional[str] = "beginner"  # e.g., "beginner", "intermediate", "expert"
    protein_source_preferences: Optional[List[str]] = None  # e.g., ["chicken", "tofu"]
    cooking_style: Optional[str] = "home_cooked"  # e.g., "home_cooked", "takeout"
    meal_preferences: Optional[List[str]] = None  # e.g., ["breakfast", "snack"]
    meal_frequency: Optional[str] = "3 meals a day"  # e.g., "2 meals a day", "5 meals a day"
    meal_time_preferences: Optional[List[str]] = None  # e.g., ["morning", "evening"]
    meal_preparation_time: Optional[str] = "30 minutes"  # e.g., "15 minutes", "1 hour"
    meal_portion_size: Optional[str] = "medium"  # e.g., "small", "large"
    salt_level_preference: Optional[str] = "medium"  # e.g., "low", "high"
    spice_level_preference: Optional[str] = "medium"  # e.g., "low", "high"
    sugar_level_preference: Optional[str] = "medium"  # e.g., "low", "high"
    sour_level_preference: Optional[str] = "medium"  # e.g., "low", "high"
    texture_preferences: Optional[List[str]] = None  # e.g., ["crispy", "smooth"]
    salt_tolerance: Optional[str] = "medium"  # e.g., "low", "high"
    spice_tolerance: Optional[str] = "medium"  # e.g., "low", "high"
    sugar_tolerance: Optional[str] = "medium"  # e.g., "low", "high"
    sour_tolerance: Optional[str] = "medium"  # e.g., "low", "high"
    texture_tolerance: Optional[str] = "medium"  # e.g., "low", "high"
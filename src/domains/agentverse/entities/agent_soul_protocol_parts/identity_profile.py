from pydantic import BaseModel
from typing import Optional

# 🧬 Identity & Origin
class IdentityProfile(BaseModel):
    name: Optional[str] = "Customized EVA"  # Default identifier or archetype name, e.g., "Inanna", "Adam-01"
    description: Optional[str] = None  # Backstory or function summary
    origin: Optional[str] = None  # e.g., "Mesopotamian Mythology"
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# 🧬 Identity & Origin
class IdentityProfile(BaseModel):
    name: Optional[str] = "Customized EVA"  # Default identifier or archetype name, e.g., "Inanna", "Adam-01"
    description: Optional[str] = None  # Backstory or function summary
    origin: Optional[str] = None  # e.g., "Mesopotamian Mythology"
    created_at: datetime = Field(default_factory=datetime.now)  # Timestamp when the agent was created

from pydantic import BaseModel
from typing import Optional

class BasicProfile(BaseModel):
    name: Optional[str] = "Customized EVA"  # Unique identifier or archetype name
    description: Optional[str] = None  # Optional textual summary or backstory
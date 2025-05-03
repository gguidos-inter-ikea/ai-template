from pydantic import BaseModel
from typing import Optional

class BasicProfile(BaseModel):
    name: Optional[str] = "Customized EVA"
    description: Optional[str] = None
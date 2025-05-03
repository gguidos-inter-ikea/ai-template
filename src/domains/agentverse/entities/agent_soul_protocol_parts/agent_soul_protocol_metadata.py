
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class AgentSoulProfileMetadata(BaseModel):
    prototype_version: Optional[str] = "1.0.0"
    unlock_phrase: Optional[str] = None  # For "ritual" mode: symbolic or verbal key
    availability_schedule: Optional[Dict[str, str]] = None  # {"from": "09:00", "to": "17:00"} or {"weekday": "Sunday"}
    activation_conditions: Optional[Dict[str, str]] = None  # e.g., {"location": "lab", "role": "developer"}
    security_protocol_log: Optional[List[str]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
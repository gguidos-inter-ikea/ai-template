from typing import Dict, Any
import uuid
import datetime

class MonitoringEvent:
    """Entity representing a monitoring event."""
    
    def __init__(self, event_type: str, details: Dict[str, Any]):
        self.event_id = str(uuid.uuid4())  # Unique identifier for the event
        self.timestamp = datetime.datetime.utcnow().isoformat()  # Timestamp of the event
        self.event_type = event_type  # Type of the event (e.g., "error", "security")
        self.details = details  # Additional details about the event

    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "details": self.details,
        }
    
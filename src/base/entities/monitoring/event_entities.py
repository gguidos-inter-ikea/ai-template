from typing import Dict, Any

class Event:
    """Base class for all events."""
    def __init__(self, event_type: str, details: Dict[str, Any]):
        self.event_type = event_type
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary."""
        return {
            "event_type": self.event_type,
            "details": self.details,
        }

class SecurityEvent(Event):
    """Event for security-related issues."""
    def __init__(self, reason: str, path: str, method: str, client_ip: str, headers: Dict[str, str], additional_info: Dict[str, Any]):
        super().__init__("security", {
            "reason": reason,
            "path": path,
            "method": method,
            "client_ip": client_ip,
            "headers": headers,
            "additional_info": additional_info,
        })

class ErrorEvent(Event):
    """Event for error-related issues."""
    def __init__(self, error_type: str, details: Dict[str, Any]):
        super().__init__("error", {
            "error_type": error_type,
            "details": details,
        })
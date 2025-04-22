from typing import Dict, List

class WebSocketRouteRegistry:
    def __init__(self):
        self.routes: Dict[str, str] = {}

    def register(self, name: str, path: str):
        self.routes[name] = path

    def all(self) -> List[Dict[str, str]]:
        return [{"name": name, "path": path} for name, path in self.routes.items()]

# Singleton instance
websocket_registry_instance = WebSocketRouteRegistry()
from typing import Dict, Any

class ReflexEngine:
    def __init__(self, preferences: Dict[str, Any]):
        self.preferences = preferences or {}

    async def process(self, stimulus: Dict[str, Any]) -> str:
        responses = []

        temp = stimulus.get("temperature")
        if temp is not None and temp < self.preferences.get("temperature_min", 18):
            responses.append("🥶 It’s cold. I’m uncomfortable.")

        if stimulus.get("loud_sound") and self.preferences.get("sound_preferences") == "low":
            responses.append("🔊 That’s too loud. Please lower your voice.")

        if not responses:
            responses.append("🧘 I feel balanced in this environment.")

        return " ".join(responses)


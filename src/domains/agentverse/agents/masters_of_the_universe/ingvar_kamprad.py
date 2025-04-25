from src.domains.agentverse.agents.base import BaseAgent
from src.domains.agentverse.registries.registries import agent_registry_instance
import logging
import json
logger = logging.getLogger("agentverse.ingvar")

@agent_registry_instance.register(
    name="ingvar_kamprad",
    description="A minimalist entrepreneur agent who summarizes content and rewrites it with Swedish simplicity.",
    version="1.0.0",
    metadata={
        "capabilities": ["summarize", "rephrase", "style-transform", "pragmatic-voice"],
        "department": "INNOVATION",
        "archetype": "Minimalist Mentor"
    }
)
class IngvarKampradAgent(BaseAgent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory_key = f"{self.id}_summary_memory"

    async def respond(self, user_input: str) -> str:
        memory_key = f"{self.id}_memory"
        history = []

        # 🔒 Safely load history from Redis
        if self.cache:
            raw = await self.cache.get(memory_key)
            try:
                history = json.loads(raw) if raw else []
            except json.JSONDecodeError:
                history = []

            history.append({"user": user_input})

        # 🧠 Compose prompt with personality context
        composed_prompt = f"{self.personality_context.strip()}\n\n{self.prompt.strip()}"

        response = self.llm.generate(
            prompt=composed_prompt,
            user_input=user_input,
            history=history
        )

        # 🔐 Safely save updated history
        if self.cache:
            history.append({"agent": response})
            await self.cache.set(memory_key, json.dumps(history))

        return response

    async def summarize_and_rewrite(self, text: str) -> str:
        """
        Standalone method to summarize and rewrite text in Kamprad’s tone.
        """
        return await self.respond(text)

    async def summarize_and_translate(self, text: str, target_language: str = "sv") -> str:
        """
        Summarize and translate the text into Swedish (or another supported language).
        """
        summary = await self.respond(text)
        if target_language.lower() != "en":
            translated = self.llm.translate(summary, target_language=target_language)
            return translated
        return summary

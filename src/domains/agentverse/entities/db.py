from pydantic import BaseModel
from typing import Optional
from src.domains.agentverse.entities.agent_soul_protocol import AgentSoulProtocol

class DBAgentPost(BaseModel):
    creator: str
    agent_id: str
    agent_name: str
    agent_type: str
    agent_prompt: str
    agent_llm_type: str
    agent_db_type: Optional[str] = None
    agent_cache_type: Optional[str] = None
    agent_knowledge_db_type: Optional[str] = None
    agent_messaging_type: Optional[str] = None
    agent_personality: AgentSoulProtocol
    agent_personality_profile: str
    agent_dna_sequence: str
    agent_chat_url: str
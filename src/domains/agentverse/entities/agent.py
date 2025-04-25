from pydantic import BaseModel, Field
from typing import Optional, Any
from src.domains.agentverse.entities.agent_soul_protocol import AgentSoulProtocol

class AgentRequest(BaseModel):
    user_id: str
    name: str
    type: str
    prompt: str
    llm_type: Optional[str] = "openai"
    db_type: Optional[str] = None
    cache_type: Optional[str] = "redis"
    knowledge_db_type: Optional[str] = None
    messaging_type: Optional[str] = None
    personality_profile: Optional[str] = Field('Mortal EVA', alias="personality_profile")
    personality: Optional[AgentSoulProtocol] = None

class AgentConfig(BaseModel):
    user_id: str
    name: str
    type: str
    prompt: str
    llm_type: str
    db_type: Optional[str]
    cache_type: Optional[str]
    knowledge_db_type: Optional[str]
    messaging_type: Optional[str]
    personality_profile: Optional[str]
    personality: Optional[AgentSoulProtocol]

class BaseAgentConfig(BaseModel):
    id: str
    creator: str
    name: str
    system_name: str
    type: str
    prompt: str
    llm: Any
    db: Optional[Any]
    cache: Optional[Any]
    vectordb: Optional[Any]
    messaging: Optional[Any]
    personality_profile: Optional[str]
    dna_sequence: str
    personality: AgentSoulProtocol
    chat_url: str

class Agent(BaseModel):
    id: str
    name: str
    system_name: str
    type: str
    prompt: str
    chat_url: str
    llm_type: str
    db_type: Optional[str]
    cache_type: Optional[str]
    knowledge_db_type: Optional[str]
    messaging_type: Optional[str]
    personality_profile: Optional[str]
    personality: AgentSoulProtocol
    dna_sequence: str

class DBAgent(BaseModel):
    user_id: str
    agent: Agent

class ChatRequest(BaseModel):
    user_id: str
    message: str


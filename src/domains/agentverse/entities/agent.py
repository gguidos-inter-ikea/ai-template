from pydantic import BaseModel, Field
from typing import Optional, Any
from src.domains.agentverse.entities.agent_soul_protocol import AgentSoulProtocol
from src.domains.agentverse.entities.tools.tool_spec import ToolSpec
from typing import List

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
    
    access_mode: str = Field(
        "public",
        description="Options: public, commander, ritual, guardian, offline"
    )
    
    public_key: Optional[str] = None  # distributed for verification
    private_key: Optional[str] = None # kept encrypted, used to sign memory, DNA merges
    whitelist_users: List[str] = Field(default_factory=list)
    blacklist_users: List[str] = Field(default_factory=list)

    personality_profile: str = Field(
        "Mortal EVA",
        description="Name of the personality profile to bind"
    )
    personality: Optional[AgentSoulProtocol] = None
    tools: List[ToolSpec] = Field(default_factory=list)

class AgentConfig(BaseModel):
    user_id: str
    name: str
    type: str
    prompt: str
    llm_type: str
    db_type: Optional[str]
    cache_type: Optional[str]
    access_mode: Optional[str] = "public"  # Options: "public", "commander", "ritual", "guardian", "offline"
    public_key: Optional[str] = None  # distributed for verification
    private_key: Optional[str] = None # kept encrypted, used to sign memory, DNA merges
    whitelist_users: Optional[List[str]] = None  # Usernames or session keys allowed
    blacklist_users: Optional[List[str]] = None  # Users explicitly denied
    knowledge_db_type: Optional[str]
    messaging_type: Optional[str]
    personality_profile: Optional[str]
    personality: Optional[AgentSoulProtocol]
    access_mode: str
    tools: Optional[List[str]] = None  # List of tool names
    public_key: Optional[str] = None  # distributed for verification
    private_key: Optional[str] = None # kept encrypted, used to sign memory, DNA merges
    whitelist_users: Optional[List[str]]  # Usernames or session keys allowed
    blacklist_users: Optional[List[str]]  # Users explicitly denied
    personality_profile: Optional[str] = Field('Mortal EVA', alias="personality_profile")
    personality: Optional[AgentSoulProtocol] = None
    tools: List[ToolSpec]  # List of tool names

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
    access_mode: str
    public_key: Optional[str] = None  # distributed for verification
    private_key: Optional[str] = None # kept encrypted, used to sign memory, DNA merges
    whitelist_users: Optional[List[str]]  # Usernames or session keys allowed
    blacklist_users: Optional[List[str]]  # Users explicitly denied
    tools: List[ToolSpec]
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
    access_mode: str # Options: "public", "commander", "ritual", "guardian", "offline"
    public_key: Optional[str] = None  # distributed for verification
    private_key: Optional[str] = None # kept encrypted, used to sign memory, DNA merges
    whitelist_users: Optional[List[str]] # Usernames or session keys allowed
    blacklist_users: Optional[List[str]] # Users explicitly denied
    dna_sequence: str
    tools: List[ToolSpec] #List of tool names

class DBAgent(BaseModel):
    user_id: str
    agent: Agent

class ChatRequest(BaseModel):
    user_id: str
    message: str


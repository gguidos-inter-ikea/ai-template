from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, PrivateAttr, computed_field
from src.base.config.ai_models_config import AiModelsConfig
from src.domains.agentverse.entities.agent_soul_protocol_parts.agent_soul_protocol import AgentSoulProtocol
from src.domains.agentverse.registries import personality_registry_instance

class AgentRequest(BaseModel):
    # --- core fields -------------------------------------------------
    user_id: str
    name: str
    type: str
    prompt: str

    # --- back-ends ---------------------------------------------------
    llm_type: str = Field(                         # <- was Optional
        default_factory=lambda: AiModelsConfig().model,
        description="Key inside app.state.cognitive_modules['llm']"
    )
    image_type: str = Field(
        default=None,
        description="Key inside app.state.cognitive_modules['image']"
    )
    video_type: str = Field(
        default=None,
        description="Key inside app.state.cognitive_modules['video']"
    )
    db_type:         Optional[str] = None
    cache_type:      Optional[str] = "redis"
    knowledge_db_type: Optional[str] = None
    messaging_type:  Optional[str] = None

    # --- security ----------------------------------------------------
    access_mode: str = Field(default="public")
    public_key:  Optional[str] = None
    private_key: Optional[str] = None
    whitelist_users: List[str] = Field(default_factory=list)
    blacklist_users: List[str] = Field(default_factory=list)

    # 2) raw delta from the UI  (whatever keys the user changed)
    personality: Dict[str, Any]      # <-- stays dict, no defaults added

    # --- tools -------------------------------------------------------
    tools: List[str] = Field(default_factory=list)

    # --- private cached full soul -----------------------------------
    _soul: AgentSoulProtocol | None = PrivateAttr(default=None)

    model_config = {"extra": "allow", "populate_by_name": True}

    # ---------- helper to get the full, hydrated soul ----------------
    @computed_field
    @property
    def soul(self) -> AgentSoulProtocol:
        """Return a cached full AgentSoulProtocol (lazy‐hydrated)."""
        if self._soul is None:
            base = personality_registry_instance.get(self.personality_archetype)()
            self._soul = base.model_copy(update=self.personality, deep=True)
        return self._soul

class AgentConfig(BaseModel):
    user_id: str
    name: str
    type: str
    prompt: str
    llm_type: str
    image_type: Optional[str]= None
    video_type: Optional[str]= None
    db_type: Optional[str]
    cache_type: Optional[str]
    access_mode: Optional[str] = "public"  # Options: "public", "commander", "ritual", "guardian", "offline"
    public_key: Optional[str] = None  # distributed for verification
    private_key: Optional[str] = None # kept encrypted, used to sign memory, DNA merges
    whitelist_users: Optional[List[str]] = None  # Usernames or session keys allowed
    blacklist_users: Optional[List[str]] = None  # Users explicitly denied
    knowledge_db_type: Optional[str]
    messaging_type: Optional[str]
    personality: AgentSoulProtocol
    access_mode: str
    tools: Optional[List[str]] = None  # List of tool names
    public_key: Optional[str] = None  # distributed for verification
    private_key: Optional[str] = None # kept encrypted, used to sign memory, DNA merges
    whitelist_users: Optional[List[str]]  # Usernames or session keys allowed
    blacklist_users: Optional[List[str]]  # Users explicitly denied
    personality: Dict[str, Any] 
    tools: List[str] = Field(default_factory=list)

class BaseAgentConfig(BaseModel):
    id: str
    creator: str
    name: str
    system_name: str
    type: str
    prompt: str
    llm: Any
    image: Optional[str]= None
    video: Optional[str]= None
    db: Optional[Any]
    cache: Optional[Any]
    vectordb: Optional[Any]
    messaging: Optional[Any]
    access_mode: str
    public_key: Optional[str] = None  # distributed for verification
    private_key: Optional[str] = None # kept encrypted, used to sign memory, DNA merges
    whitelist_users: Optional[List[str]]  # Usernames or session keys allowed
    blacklist_users: Optional[List[str]]  # Users explicitly denied
    tools: List[str] = Field(default_factory=list)
    dna_sequence: str
    personality: Dict[str, Any]
    chat_url: str

class Agent(BaseModel):
    id: str
    name: str
    system_name: str
    type: str
    prompt: str
    chat_url: str
    llm_type: str
    image_type: Optional[str]= None
    video_type: Optional[str]= None
    db_type: Optional[str]
    cache_type: Optional[str]
    knowledge_db_type: Optional[str]
    messaging_type: Optional[str]
    personality: Dict[str, Any]
    access_mode: str # Options: "public", "commander", "ritual", "guardian", "offline"
    public_key: Optional[str] = None  # distributed for verification
    private_key: Optional[str] = None # kept encrypted, used to sign memory, DNA merges
    whitelist_users: Optional[List[str]] # Usernames or session keys allowed
    blacklist_users: Optional[List[str]] # Users explicitly denied
    dna_sequence: str
    tools: List[str] = Field(default_factory=list)

class DBAgent(BaseModel):
    user_id: str
    agent: Agent

class ChatRequest(BaseModel):
    user_id: str
    message: str


from pydantic import BaseModel, ConfigDict
from src.domains.agentverse.entities.agent_soul_protocol_parts.identity_profile import IdentityProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.cognitive_profile import CognitiveProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.culinary_profile import CulinaryProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.cultural_profile import CulturalProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.economic_profile import EconomicProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.expression_profile import ExpressionProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.personal_profile import PersonalProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.sensory_profile import SensoryProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.simulation_profile import SimulationProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.spiritual_profile import SpiritualProfile

class agent_soul_protocol(BaseModel):
    """
    Agent Soul Protocol (ASP) - The core framework for agent creation and management.
    
    This module defines the structure and behavior of agents within the AgentVerse.
    It includes the identity profile, memory management, and interaction protocols.
    
    Attributes:
        identity_profile (IdentityProfile): The identity and origin of the agent.
        memory (Memory): The memory management system for the agent.
        interaction_protocol (InteractionProtocol): The communication and interaction methods.
    """
    

    
    cognitive_profile = CognitiveProfile
    culinary_profile = CulinaryProfile
    cultural_profile = CulturalProfile
    economic_profile = EconomicProfile
    expression_profile = ExpressionProfile
    identity_profile = IdentityProfile
    personal_profile = PersonalProfile
    sensory_profile = SensoryProfile
    simulation_profile = SimulationProfile
    spiritual_profile = SpiritualProfile

    model_config = ConfigDict(extra="allow")

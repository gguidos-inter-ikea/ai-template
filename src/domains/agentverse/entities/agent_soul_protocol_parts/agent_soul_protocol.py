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


class AgentSoulProtocol(BaseModel):
    """
    Agent Soul Protocol (ASP) - The core framework for agent creation and management.
    """

    cognitive_profile: CognitiveProfile = CognitiveProfile()
    culinary_profile: CulinaryProfile = CulinaryProfile()
    cultural_profile: CulturalProfile = CulturalProfile()
    economic_profile: EconomicProfile = EconomicProfile()
    expression_profile: ExpressionProfile = ExpressionProfile()
    identity_profile: IdentityProfile = IdentityProfile()
    personal_profile: PersonalProfile = PersonalProfile()
    sensory_profile: SensoryProfile = SensoryProfile()
    simulation_profile: SimulationProfile = SimulationProfile()
    spiritual_profile: SpiritualProfile = SpiritualProfile()

    model_config: ConfigDict = ConfigDict(extra="allow")

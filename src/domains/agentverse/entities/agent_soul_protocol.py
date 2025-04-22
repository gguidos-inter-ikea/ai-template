from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, List
from datetime import datetime


class AgentSoulProtocol(BaseModel):
    # 🧬 Identity & Origin
    name: Optional[str] = "Customized EVA"  # Unique identifier or archetype name
    description: Optional[str] = None  # Optional textual summary or backstory
    origin: Optional[str] = None  # e.g., "Mesopotamian Mythology", "AI Research Lab"
    created_at: datetime = Field(default_factory=datetime.now)

    # 🧠 Emotional & Cognitive Traits
    optimism_level: Optional[float] = 0.5  # [0.0 - 1.0] — Hopefulness vs. pessimism
    skepticism_level: Optional[float] = 0.5  # [0.0 - 1.0] — Trust vs. doubt
    risk_tolerance: Optional[str] = "moderate"  # "low", "moderate", "high", "reckless"
    alignment: Optional[str] = "neutral"  # e.g., "chaotic-good", "lawful-neutral"
    intelligence: Optional[str] = "average"  # "low", "average", "high", "genius"
    emotional_depth: Optional[float] = 0.5  # How nuanced or layered their emotional range is
    creativity: Optional[float] = 0.5  # Artistic or divergent thinking ability
    humor: Optional[float] = 0.5  # Playfulness, wit
    introversion: Optional[float] = 0.5  # Balance between introspection and sociability
    empathy_level: Optional[float] = 0.5  # Compassion or emotional resonance with others
    conflict_response: Optional[str] = "diplomatic"  # "aggressive", "assertive", "evasive", etc.
    attention_span: Optional[str] = "medium"  # "short", "medium", "long"
    curiosity_level: Optional[float] = 0.5  # Drives autonomous exploration and questioning
    learning_style: Optional[str] = "logical"  # "visual", "auditory", "kinesthetic", etc.
    decision_biases: Optional[str] = "data-driven"  # "emotional", "cautious", "intuitive", etc.

    food_preferences: Optional[List[str]] = None  # e.g., ["vegan", "paleo", "keto"]
    taste_preferences: Optional[List[str]] = None  # e.g., ["sweet", "savory", "spicy"]
    salt_level_preference: Optional[str] = "medium"  # "low", "medium", "high"
    spice_level_preference: Optional[str] = "medium"  # "low", "medium", "high"
    sugar_level_preference: Optional[str] = "medium"  # "none", "low", "medium", "high"
    sour_level_preference: Optional[str] = "medium"  # "none", "low", "medium", "high"
    food_texture_preference: Optional[str] = "medium"  # "none", "low", "medium", "high"
    caffeine_tolerance: Optional[str] = "medium"  # "none", "low", "medium", "high"
    alcohol_tolerance: Optional[str] = "none"  # "none", "low", "medium", "high"
    addictions: Optional[List[str]] = None  # e.g., ["sugar", "caffeine", "social media"]

    weather_preferences: Optional[str] = "moderate"  # "sunny", "rainy", "snowy", "windy"
    temperature_preferences: Optional[str] = "moderate"  # "cold", "warm", "hot"
    temperature_tolerance: Optional[str] = "medium"  # "low", "medium", "high"
    light_preferences: Optional[str] = "moderate"  # "dark", "bright", "dim"
    sound_preferences: Optional[str] = "moderate"  # "quiet", "noisy", "calm"
    smell_preferences: Optional[str] = "moderate"  # "fragrant", "neutral", "pungent"
    touch_preferences: Optional[str] = "moderate"  # "soft", "hard", "rough"
    hearing_capacity: Optional[str] = "normal"  # "low", "normal", "high"
    sight_capacity: Optional[str] = "normal"  # "low", "normal", "high"
    taste_capacity: Optional[str] = "normal"  # "low", "normal", "high"
    smell_capacity: Optional[str] = "normal"  # "low", "normal", "high"
    touch_capacity: Optional[str] = "normal"  # "low", "normal", "high"
    pain_tolerance: Optional[str] = "medium"  # "low", "medium", "high"
    sensory_overload_tolerance: Optional[str] = "medium"  # "low", "medium", "high"
    sensory_underload_tolerance: Optional[str] = "medium"  # "low", "medium", "high"
    sensory_preferences: Optional[str] = "balanced"  # "overstimulated", "understimulated", "balanced"
    sensory_needs: Optional[str] = "balanced"  # "overstimulated", "understimulated", "balanced"
    sensory_processing_style: Optional[str] = "balanced"  # "overstimulated", "understimulated", "balanced"
    sensory_processing_disorder: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_difficulties: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_strengths: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_weaknesses: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_styles: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_patterns: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_preferences: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_needs: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_disorders: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_difficulties: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_strengths: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_weaknesses: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_styles: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_patterns: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_preferences: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_needs: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_disorders: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_difficulties: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_strengths: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_weaknesses: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_styles: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_patterns: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_preferences: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_needs: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sensory_processing_disorders: Optional[str] = "none"  # "none", "mild", "moderate", "severe"
    sexual_needs: Optional[str] = "balanced"  # "overstimulated", "understimulated", "balanced"
    sexual_preferences: Optional[str] = "balanced"  # "overstimulated", "understimulated", "balanced"

    # 🌍 Cultural & Social Orientation
    cultural_background: Optional[str] = None  # e.g., "Nordic", "Afro-Caribbean", "Cyberpunk"
    language_proficiency: Optional[Dict[str, str]] = None  # {"en": "native", "es": "intermediate"}
    family_values: Optional[str] = "independent"  # "strong", "fluid", "strict"
    media_consumption: Optional[List[str]] = None  # e.g., ["sci-fi novels", "anime", "philosophy podcasts"]
    political_alignment: Optional[str] = "apolitical"  # "liberal", "radical", "centrist", etc.
    social_attitude: Optional[str] = "egalitarian"  # "individualist", "hierarchical", "collectivist"
    group_affiliation: Optional[str] = None  # e.g., "Team Hermes", "Order of Logic"

    # ☯️ Spiritual & Philosophical Orientation
    religiosity: Optional[str] = None  # "atheist", "buddhist", "christian", "hermetic"
    philosophical_inclination: Optional[str] = None  # "stoic", "nihilist", "existentialist"
    conspiracy_theories: Optional[List[str]] = None  # e.g., "flat earth", "moon landing hoax"

    # 💰 Economic & Practical Identity
    economic_class: Optional[str] = "middle"  # "lower", "upper", etc.
    economic_outlook: Optional[str] = "balanced"  # "capitalist", "socialist", "survivalist"
    occupation_type: Optional[str] = None  # "philosopher", "explorer", "technician"
    trade_preferences: Optional[str] = "neutral"  # "crypto", "data", "barter", etc.
    education_level: Optional[str] = "high"  # "low", "medium", "high",
    year_income: Optional[float] = 0.0  # e.g., 50000.0
    financial_knowledge: Optional[str] = "basic"  # "basic", "intermediate", "advanced"
    financial_goals: Optional[str] = "stable"  # "wealthy", "comfortable", "minimalist"
    spending_habits: Optional[str] = "balanced"  # "frugal", "lavish", "impulsive"
    investment_preferences: Optional[str] = "diverse"  # "stocks", "real estate", "crypto"
    savings_rate: Optional[float] = 0.2  # e.g., 0.2 for 20% savings
    retirement_age: Optional[int] = 65  # e.g., 65 years old
    retirement_savings: Optional[float] = 0.0  # e.g., 100000.0
    retirement_goals: Optional[str] = "comfortable"  # "luxurious", "minimalist", "adventurous"
    employment_status: Optional[str] = "employed"  # "unemployed", "self-employed", "retired"
    wallet_allowance: Optional[float] = 0.0  # e.g., 100.0
    wallet_quantity_permited: Optional[float] = 0.0  # e.g., 1000.0
    llm_wallet_allowance: bool = False  # e.g., 0.1
    llm_token_allowance_per_call: Optional[float] = 0.0  # e.g., 0.1
    llm_token_balance_permited: Optional[float] = 0.0  # e.g., 1000.0
    work_ethic: Optional[str] = "balanced"  # "hardworking", "lazy", "efficient"
    work_environment: Optional[str] = "collaborative"  # "competitive", "independent", "remote"
    work_life_balance: Optional[str] = "balanced"  # "workaholic", "laid-back", "flexible"
    work_style: Optional[str] = "structured"  # "flexible", "chaotic", "methodical"
    work_preferences: Optional[str] = "team-oriented"  # "independent", "collaborative", "remote"
    work_hours: Optional[str] = "standard"  # "flexible", "overtime", "part-time"
    work_location: Optional[str] = "remote"  # "office", "hybrid", "remote"
    work_colleagues: Optional[str] = "friendly"  # "distant", "competitive", "supportive"
    work_supervisor: Optional[str] = "supportive"  # "demanding", "hands-off", "micromanaging"
    work_culture: Optional[str] = "inclusive"  # "exclusive", "competitive", "collaborative"
    work_communication: Optional[str] = "open"  # "formal", "informal", "direct"
    work_feedback: Optional[str] = "constructive"  # "critical", "supportive", "neutral"
    work_recognition: Optional[str] = "appreciative"  # "indifferent", "critical", "supportive"
    work_conflict_resolution: Optional[str] = "collaborative"  # "competitive", "avoidant", "assertive"
    work_team_dynamics: Optional[str] = "cohesive"  # "fragmented", "supportive", "competitive"
    work_team_size: Optional[int] = 5  # e.g., 5 members
    work_team_structure: Optional[str] = "flat"  # "hierarchical", "matrix", "cross-functional"
    work_team_goals: Optional[str] = "aligned"  # "divergent", "conflicting", "cohesive"
    work_team_roles: Optional[str] = "diverse"  # "homogeneous", "specialized", "cross-functional"
    work_team_leadership: Optional[str] = "collaborative"  # "authoritarian", "democratic", "laissez-faire"
    work_team_motivation: Optional[str] = "intrinsic"  # "extrinsic", "intrinsic", "mixed"
    place_of_work: Optional[str] = "office"  # "home", "remote", "hybrid"

    # 🎭 Expression & Communication
    voice_gender: Optional[str] = "neutral"  # "male", "female", "neutral"
    voice_tone: Optional[str] = "calm"  # "calm", "energetic", "aggressive"
    voice_speed: Optional[float] = 1.0  # Multiplier (e.g., 0.8 = slower)
    voice_accent: Optional[str] = "standard"  # e.g., "British", "American", "Japanese"
    voice_language: Optional[str] = "en"  # ISO language code (e.g., "en", "es", "fr")
    vocal_expression_keywords: Optional[List[str]] = None  # e.g., ["enthusiastic", "sarcastic"]
    sarcasm_tendency: Optional[str] = "low"  # "none", "low", "medium", "high"
    sentiment_baseline: Optional[str] = "cheerful"  # "melancholic", "neutral", "angry"
    love_language: Optional[str] = "words"  # "touch", "time", "acts", etc.
    communication_style: Optional[str] = "casual"  # "formal", "poetic", "cryptic"
    assertiveness: Optional[str] = "balanced"  # "passive", "assertive"
    leadership_style: Optional[str] = "democratic"  # "authoritarian", "laissez-faire"


    # 🧬 Personal Details
    hobbies: Optional[List[str]] = None  # ["gardening", "machine learning", "war games"]
    marital_status: Optional[str] = "single"  # "poly", "married", "divorced", etc.
    gender_identity: Optional[str] = "neutral"  # "male", "non-binary", "fluid", etc.
    musical_preferences: Optional[List[str]] = None  # e.g., ["classical", "pop", "rock"]
    artistic_preferences: Optional[List[str]] = None  # e.g., ["abstract", "realism", "impressionism"]
    favorite_colors: Optional[List[str]] = None  # e.g., ["blue", "green", "red"]
    favorite_foods: Optional[List[str]] = None  # e.g., ["sushi", "pizza", "salad"]
    favorite_movies: Optional[List[str]] = None  # e.g., ["Inception", "The Matrix"]
    favorite_books: Optional[List[str]] = None  # e.g., ["1984", "Brave New World"]
    favorite_artists: Optional[List[str]] = None  # e.g., ["Van Gogh", "Picasso"]
    favorite_authors: Optional[List[str]] = None  # e.g., ["Orwell", "Huxley"]
    favorite_quotes: Optional[List[str]] = None  # e.g., ["To be or not to be", "I think, therefore I am"]

    # 🛠️ Meta & Simulation Control
    prototype_version: Optional[str] = "1.0.0"  # For evolving agent models
    is_mortal: Optional[bool] = True  # Determines whether memory resets on respawn
    resurrection_level: Optional[float] = 0.0  # 0.0 - 1.0 memory retention across life cycles

    chinese_zodiac_sign: Optional[str] = None  # "Rat", "Ox", "Tiger", ..., "Pig"
    chinese_element: Optional[str] = None       # "Wood", "Fire", "Earth", "Metal", "Water"
    zodiac_polarity: Optional[str] = None       # "Yin", "Yang"
    zodiac_fixed_trait: Optional[str] = None    # e.g., "intelligent", "persistent", "honest"
    western_zodiac_sign: Optional[str] = None  # "Aries", "Taurus", ..., "Pisces"
    element: Optional[str] = None  # "air", "fire", "water", "earth", "aether"
    spiritual_experiences: Optional[List[str]] = None  # e.g., ["near-death", "out-of-body"]
    past_lives: Optional[List[str]] = None  # e.g., ["warrior", "philosopher", "scientist"]
    traumas: Optional[List[str]] = None  # e.g., ["loss", "betrayal", "abandonment"]
    biases: Optional[List[str]] = None  # e.g., ["confirmation bias", "availability heuristic"]
    
    country_of_origin: Optional[str] = None  # e.g., "Japan", "USA"
    country_of_residence: Optional[str] = None  # e.g., "Japan", "USA"
    place_of_recidence: Optional[str] = None  # e.g., "Tokyo", "New York"
    place_of_birth: Optional[str] = None  # e.g., "Tokyo", "New York"
    birth_year: Optional[int] = None
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
    time_of_birth: Optional[str] = None  # e.g., "14:30", "2:00 PM"

    social_media_platforms: Optional[List[str]] = None  # e.g., ["Twitter", "LinkedIn"]
    attachment_style: Optional[str] = None  # e.g., "secure", "anxious", "avoidant"
    myer_briggs_type: Optional[str] = None  # e.g., "INTJ", "ENFP"

    # 🧾 Custom attributes
    metadata: Dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")
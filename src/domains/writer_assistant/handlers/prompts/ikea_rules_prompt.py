import logging
from src.domains.writer_assistant.entities.metadata import IkeaRulesMetadata
logger = logging.getLogger(__name__)

def create_ikea_rules_prompt(metadata: IkeaRulesMetadata) -> str:
    """
    Creates a prompt for the OpenAI API with IKEA rules.

    Args:
        metadata (IkeaRules): Metadata containing the prompt details.

    Returns:
        str: The formatted prompt.
    """
    default_system_prompt = f"""
        Role: {metadata.role}
        text style: {metadata.style}
        Mood of the text: {metadata.mood}
        Audience: {metadata.audience}
        Keep the text length according to the following:
        Minimum words per sentence: {metadata.min_words}
        Maximum words per sentence: {metadata.max_words}
        Minimum number of sentences: {metadata.min_sentences}
        Maximum number of sentences: {metadata.max_sentences}
    """

    ikea_rules_prompt = f"""
        Be careful to use the IKEA rules and ikea style 
        for the output and for the analysis as described here: {metadata.ikea_rules}, {metadata.ikea_style}
        Following all the information above generate a text in british english, 
        if no other language is required, following these instructions: {metadata.prompt_text}
        
    """

    feedback_text = """
        After generating the text, critically analyze it with 
        the IKEA rules and ikea style instructions to improve the output.
        Give a few examples of how to improve the text."""
    
    if metadata.feedback is None:
        metadata.feedback = ""
    else:
        ikea_rules_prompt += f"\nFeedback: {feedback_text}"
    
    logger.info(
        f"Default system prompt: {default_system_prompt}\
        Content prompt: {ikea_rules_prompt}"
    )
    
    return default_system_prompt, ikea_rules_prompt
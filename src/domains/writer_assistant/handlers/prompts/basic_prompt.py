import logging
from src.domains.writer_assistant.entities.metadata import BasicPromptMetadata
logger = logging.getLogger(__name__)

def create_prompt(metadata: BasicPromptMetadata) -> str:
    """
    Creates a prompt for the OpenAI API.

    Args:
        metadata (Metadata): Metadata containing the prompt details.

    Returns:
        str: The formatted prompt.
    """
    default_system_prompt = f"""
        Role: {metadata.role}
        text style: {metadata.style}
        Mood of the text: {metadata.mood}
        Keep the text length according to the following:
        Minimum words per sentence: {metadata.min_words}
        Maximum words per sentence: {metadata.max_words}
        Minimum number of sentences: {metadata.min_sentences}
        Maximum number of sentences: {metadata.max_sentences}
    """

    content_prompt = f"""
        Following all the information above generate a text in british english,
        if no other language is required, following these instructions: { metadata.prompt_text}        
    """

    feedback_text = """
        After generating the text, critically analyse it with the given style,
        audience, kind, purpose and greenwashing to improve the output.
    """
    
    if metadata.feedback is None:
        metadata.feedback = ""
    else:
        content_prompt += f"\nFeedback: {feedback_text}"
            
    return default_system_prompt, content_prompt
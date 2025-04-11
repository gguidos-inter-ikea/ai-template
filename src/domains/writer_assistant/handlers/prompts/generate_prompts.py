from src.domains.writer_assistant.handlers.prompts.basic_prompt import (
    create_prompt
)
from src.domains.writer_assistant.handlers.prompts.ikea_rules_prompt import (
    create_ikea_rules_prompt
)
from src.domains.writer_assistant.handlers.prompts.libs.prompt import (
    get_ikea_rules,
    get_ikea_style
)
from src.domains.writer_assistant.entities.metadata import (
    Metadata,
    IkeaRulesMetadata,
    BasicPromptMetadata
)
import logging
logger = logging.getLogger(__name__)

def generate_prompts(metadata: Metadata):
    """
    Generates prompts based on the metadata provided.

    Args:
        metadata (Metadata): Metadata containing the prompt details.

    Returns:
        str: The formatted prompt.
    """
    logger.info(f"Metadata: {metadata}")
    if metadata.ikea_rules is not None or metadata.ikea_style != []:
        logger.info("IKEA rules or style provided, using IKEA prompt.")
        if metadata.ikea_rules:
            ikea_rules_prompt = str(get_ikea_rules())  # Should return a list of strings
        else:
            ikea_rules_prompt = ""
        if metadata.ikea_style != []:
            ikea_style_prompt = str(get_ikea_style(metadata.ikea_style)) # Should return a list of strings
        else:
            ikea_style_prompt = ""

        ikea_metadata = {
            "role": metadata.role,
            "style": metadata.style,
            "mood": metadata.mood,
            "audience": metadata.audience,
            "prompt_text": metadata.prompt_text,
            "ikea_rules_promt": ikea_rules_prompt,
            "ikea_style_prompt": ikea_style_prompt,
            "feedback": metadata.feedback,
            "min_words": metadata.min_words,
            "max_words": metadata.max_words,
            "min_sentences": metadata.min_sentences,
            "max_sentences": metadata.max_sentences,
        }

        logger.info(f"ikea_metadata: {ikea_metadata}")
        ikea_metadata_obj = IkeaRulesMetadata(**ikea_metadata)
        default_system_prompt, content_prompt = create_ikea_rules_prompt(ikea_metadata_obj)
    else:
        logger.info("No IKEA rules or style provided, using basic prompt.")

        prompt_metadata = {
            "role": metadata.role,
            "style": metadata.style,
            "mood": metadata.mood,
            "audience": metadata.audience,
            "prompt_text": metadata.prompt_text,
            "feedback": metadata.feedback,
            "min_words": metadata.min_words,
            "max_words": metadata.max_words,
            "min_sentences": metadata.min_sentences,
            "max_sentences": metadata.max_sentences,
        }
        prompt_metadata_obj = BasicPromptMetadata(**prompt_metadata)
        default_system_prompt, content_prompt = create_prompt(prompt_metadata_obj)

        return default_system_prompt, content_prompt
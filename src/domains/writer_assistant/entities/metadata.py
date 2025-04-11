from typing import List, Optional
from pydantic import BaseModel

class Metadata(BaseModel):
    role: str
    style: str
    mood: str
    audience: str
    feedback: str
    prompt_text: str
    ikea_rules: Optional[List[str]] = None
    ikea_style: Optional[List[str]] = []
    max_char_length: Optional[int] = None
    min_words: int
    max_words: int
    min_sentences: int
    max_sentences: int

class RequestData(BaseModel):
    """
    Request model for sending a message to the writer assistant.
    """
    role: str
    style: str
    mood: str
    audience: str
    ikea_rules: Optional[List[str]] = None
    ikea_style: Optional[List[str]] = []
    feedback: str
    max_char_length: int
    min_words: int
    max_words: int
    min_sentences: int
    max_sentences: int
    chat: str
    prompt_text: str

class BasicPromptMetadata(BaseModel):
    role: str
    style: str
    mood: str
    audience: str
    prompt_text: str
    feedback: str
    min_words: int
    max_words: int
    min_sentences: int
    max_sentences: int

class IkeaRulesMetadata(BaseModel):
    role: str
    style: str
    mood: str
    audience: str
    prompt_text: str 
    ikea_rules_prompt: Optional[str] = ""
    ikea_style_prompt: Optional[str] = ""
    feedback: str
    min_words: int
    max_words: int
    min_sentences: int
    max_sentences: int

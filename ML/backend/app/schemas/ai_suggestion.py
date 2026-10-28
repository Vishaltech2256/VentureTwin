"""Backward-compatible exports for AI suggestion schemas."""

from app.schemas.ai_suggestions import (
    AISuggestionGenerationResponse,
    AISuggestionResponse,
    SuggestionCategory,
    SuggestionPriority,
)

__all__ = [
    "AISuggestionGenerationResponse",
    "AISuggestionResponse",
    "SuggestionCategory",
    "SuggestionPriority",
]

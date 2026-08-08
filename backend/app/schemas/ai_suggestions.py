"""Pydantic schemas for AI suggestions."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SuggestionPriority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SuggestionCategory(str, Enum):
    FINANCE = "Finance"
    MARKETING = "Marketing"
    OPERATIONS = "Operations"
    HIRING = "Hiring"
    GROWTH = "Growth"
    INVESTMENT = "Investment"


class AISuggestionResponse(BaseModel):
    """A persisted AI recommendation returned by the API."""

    suggestion_id: int = Field(..., examples=[1])
    startup_id: int = Field(..., examples=[5])
    prediction_id: int = Field(..., examples=[12])
    title: str = Field(..., examples=["Reduce operational expenses"])
    description: str = Field(
        ...,
        examples=[
            "Review recurring spending, reduce non-essential costs, and improve cash flow."
        ],
    )
    priority: SuggestionPriority = Field(..., examples=[SuggestionPriority.HIGH])
    category: SuggestionCategory = Field(..., examples=[SuggestionCategory.FINANCE])
    created_at: datetime

    model_config = {"from_attributes": True}


class AISuggestionGenerationResponse(BaseModel):
    """Result of generating suggestions for the latest startup prediction."""

    startup_id: int = Field(..., examples=[5])
    prediction_id: int = Field(..., examples=[12])
    generated_count: int = Field(..., examples=[3])
    suggestions: list[AISuggestionResponse]

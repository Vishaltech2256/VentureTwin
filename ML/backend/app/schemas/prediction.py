# app/schemas/prediction.py

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class PredictionCreate(BaseModel):
    """Internal schema used by the service layer when persisting a new prediction."""

    startup_id: int = Field(..., description="ID of the startup for which the prediction was generated")
    revenue_prediction: float = Field(..., description="Projected annual revenue (expected_monthly_revenue × 12)")
    profit_prediction: float = Field(..., description="Projected annual profit (revenue − annual expenses)")
    risk_level: str = Field(..., description="Calculated risk classification: High | Medium | Low")
    health_score: float = Field(..., description="Composite health score (0–100)")


class PredictionResponse(BaseModel):
    """
    Schema returned by all prediction endpoints.

    All monetary fields are rounded to 2 decimal places for readability.
    The `health_score` is capped between 0 and 100.
    """

    prediction_id: int = Field(
        ...,
        description="Unique identifier of the prediction record",
        examples=[1],
    )
    startup_id: int = Field(
        ...,
        description="ID of the startup this prediction belongs to",
        examples=[5],
    )
    revenue_prediction: float = Field(
        ...,
        description="Projected annual revenue",
        examples=[180000.00],
    )
    profit_prediction: float = Field(
        ...,
        description="Projected annual profit (may be negative for high-risk startups)",
        examples=[84000.00],
    )
    risk_level: str = Field(
        ...,
        description="Risk classification: High | Medium | Low",
        examples=["Medium"],
    )
    health_score: float = Field(
        ...,
        description="Composite health score between 0 and 100",
        examples=[90.00],
    )
    created_at: datetime = Field(
        ...,
        description="UTC timestamp when the prediction was generated",
    )

    model_config = {"from_attributes": True}

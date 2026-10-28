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
        description="Projected annual revenue (deterministic formula: expected_monthly_revenue × 12)",
        examples=[180000.00],
    )
    profit_prediction: float = Field(
        ...,
        description="Projected annual profit (deterministic formula: revenue − annual expenses)",
        examples=[84000.00],
    )
    risk_level: str = Field(
        ...,
        description="Formula-based risk classification: High | Medium | Low",
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

    # Machine Learning evaluation fields (evaluated via XGBoost against historical resolved cohorts)
    relative_success_likelihood: Optional[float] = Field(
        default=None,
        description="Machine Learning Relative Success Likelihood (0.0 to 1.0, evaluated against historical resolved ventures). NOT an absolute success probability.",
        examples=[0.2291],
    )
    relative_likelihood_percentage: Optional[str] = Field(
        default=None,
        description="Relative Success Likelihood formatted as a percentage string",
        examples=["22.9%"],
    )
    relative_classification: Optional[str] = Field(
        default=None,
        description="Relative Likelihood classification category",
        examples=["Moderate/Low Relative Likelihood"],
    )
    ml_model_evaluation: Optional[dict] = Field(
        default=None,
        description="Detailed ML model evaluation breakdown including factors, recommendations, and interpretation note",
    )
    warnings: Optional[list[str]] = Field(
        default=None,
        description="Plain-English warnings regarding sector fallbacks, location proxies, or domain constraints",
    )

    model_config = {"from_attributes": True}


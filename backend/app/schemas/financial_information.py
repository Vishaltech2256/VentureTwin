# app/schemas/financial_information.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class FinancialInformationCreate(BaseModel):
    """Schema for creating a new financial information record."""

    startup_id: int = Field(
        ...,
        description="ID of the startup this financial info belongs to",
        examples=[1]
    )
    initial_budget: float = Field(
        ...,
        ge=0,
        description="Initial budget allocated for the startup (must be >= 0)",
        examples=[50000.00]
    )
    monthly_expenses: float = Field(
        ...,
        ge=0,
        description="Estimated monthly operating expenses (must be >= 0)",
        examples=[8000.00]
    )
    expected_monthly_revenue: float = Field(
        ...,
        ge=0,
        description="Target monthly recurring revenue - MRR (must be >= 0)",
        examples=[15000.00]
    )
    funding_source: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Primary source of funding (cannot be empty)",
        examples=["Angel Round"]
    )

    @field_validator("funding_source")
    @classmethod
    def funding_source_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("funding_source cannot be empty or whitespace")
        return v.strip()


class FinancialInformationUpdate(BaseModel):
    """Schema for partially updating an existing financial information record."""

    initial_budget: Optional[float] = Field(
        default=None,
        ge=0,
        description="Updated initial budget (must be >= 0 if provided)",
        examples=[60000.00]
    )
    monthly_expenses: Optional[float] = Field(
        default=None,
        ge=0,
        description="Updated monthly expenses (must be >= 0 if provided)",
        examples=[9000.00]
    )
    expected_monthly_revenue: Optional[float] = Field(
        default=None,
        ge=0,
        description="Updated expected monthly revenue (must be >= 0 if provided)",
        examples=[18000.00]
    )
    funding_source: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated funding source (cannot be empty if provided)",
        examples=["Seed VC"]
    )

    @field_validator("funding_source")
    @classmethod
    def funding_source_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("funding_source cannot be empty or whitespace")
            return v.strip()
        return v


class FinancialInformationResponse(BaseModel):
    """Schema returned in API responses for financial information."""

    financial_id: int = Field(..., description="Unique identifier of the financial record")
    startup_id: int = Field(..., description="ID of the related startup profile")
    initial_budget: float = Field(..., description="Initial budget allocated for the startup")
    monthly_expenses: float = Field(..., description="Monthly operating expenses")
    expected_monthly_revenue: float = Field(..., description="Expected monthly revenue")
    funding_source: str = Field(..., description="Primary funding source")
    created_at: datetime = Field(..., description="Timestamp when the record was created")

    model_config = {"from_attributes": True}

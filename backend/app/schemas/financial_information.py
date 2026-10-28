# app/schemas/financial_information.py

from datetime import datetime, timezone
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator, AliasChoices, computed_field


class FinancialInformationCreate(BaseModel):
    """Schema for creating a new financial information record."""

    startup_id: Optional[int] = Field(
        default=None,
        description="ID of the startup this financial info belongs to (optional if provided in URL)",
        examples=[1]
    )
    initial_budget: Optional[float] = Field(
        default=0.0,
        ge=0,
        validation_alias=AliasChoices("initial_budget", "initial_investment"),
        description="Initial budget allocated for the startup (must be >= 0)",
        examples=[50000.00]
    )
    monthly_expenses: Optional[float] = Field(
        default=0.0,
        ge=0,
        description="Estimated monthly operating expenses (must be >= 0)",
        examples=[8000.00]
    )
    expected_monthly_revenue: Optional[float] = Field(
        default=0.0,
        ge=0,
        validation_alias=AliasChoices("expected_monthly_revenue", "monthly_revenue"),
        description="Target monthly recurring revenue - MRR (must be >= 0)",
        examples=[15000.00]
    )
    funding_source: Optional[str] = Field(
        default="Self-Funded",
        max_length=100,
        validation_alias=AliasChoices("funding_source", "funding_raised"),
        description="Primary source of funding",
        examples=["Angel Round"]
    )
    annual_revenue: Optional[float] = Field(default=None, ge=0)
    annual_profit: Optional[float] = Field(default=None)
    burn_rate: Optional[float] = Field(default=None, ge=0)
    funding_raised: Optional[float] = Field(default=None, ge=0)

    model_config = {"populate_by_name": True}

    @field_validator("funding_source", mode="before")
    @classmethod
    def coerce_funding_source(cls, v: Any) -> str:
        if v is None:
            return "Self-Funded"
        if isinstance(v, (int, float)):
            return f"Funding: {v:,.0f}" if v > 0 else "Bootstrapped"
        s = str(v).strip()
        return s if s else "Self-Funded"


class FinancialInformationUpdate(BaseModel):
    """Schema for partially updating an existing financial information record."""

    initial_budget: Optional[float] = Field(
        default=None,
        ge=0,
        validation_alias=AliasChoices("initial_budget", "initial_investment"),
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
        validation_alias=AliasChoices("expected_monthly_revenue", "monthly_revenue"),
        description="Updated expected monthly revenue (must be >= 0 if provided)",
        examples=[18000.00]
    )
    funding_source: Optional[str] = Field(
        default=None,
        max_length=100,
        validation_alias=AliasChoices("funding_source", "funding_raised"),
        description="Updated funding source",
        examples=["Seed VC"]
    )
    annual_revenue: Optional[float] = Field(default=None, ge=0)
    annual_profit: Optional[float] = Field(default=None)
    burn_rate: Optional[float] = Field(default=None, ge=0)
    funding_raised: Optional[float] = Field(default=None, ge=0)

    model_config = {"populate_by_name": True}

    @field_validator("funding_source", mode="before")
    @classmethod
    def coerce_funding_source_update(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return f"Funding: {v:,.0f}" if v > 0 else "Bootstrapped"
        s = str(v).strip()
        return s if s else None


class FinancialInformationResponse(BaseModel):
    """Schema returned in API responses for financial information."""

    financial_id: int = Field(..., description="Unique identifier of the financial record")
    startup_id: int = Field(..., description="ID of the related startup profile")
    initial_budget: Optional[float] = Field(default=0.0, description="Initial budget allocated for the startup")
    monthly_expenses: Optional[float] = Field(default=0.0, description="Monthly operating expenses")
    expected_monthly_revenue: Optional[float] = Field(default=0.0, description="Expected monthly revenue")
    funding_source: Optional[str] = Field(default="Self-Funded", description="Primary funding source")
    created_at: datetime = Field(..., description="Timestamp when the record was created")
    updated_at: Optional[datetime] = Field(default=None, description="Timestamp when the record was last updated")

    @computed_field
    @property
    def initial_investment(self) -> Optional[float]:
        return self.initial_budget

    @computed_field
    @property
    def monthly_revenue(self) -> Optional[float]:
        return self.expected_monthly_revenue

    @computed_field
    @property
    def annual_revenue(self) -> Optional[float]:
        return (self.expected_monthly_revenue or 0.0) * 12.0

    @computed_field
    @property
    def annual_profit(self) -> Optional[float]:
        rev = (self.expected_monthly_revenue or 0.0) * 12.0
        exp = (self.monthly_expenses or 0.0) * 12.0
        return rev - exp

    @computed_field
    @property
    def funding_raised(self) -> Optional[float]:
        return self.initial_budget

    @computed_field
    @property
    def burn_rate(self) -> Optional[float]:
        return self.monthly_expenses

    model_config = {"from_attributes": True, "populate_by_name": True}


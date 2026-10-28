"""Pydantic schemas for startup business reports."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReportGenerationResponse(BaseModel):
    """Metadata returned after report generation completes."""

    message: str = Field(
        ...,
        examples=["Report generated successfully"],
    )
    report_id: int = Field(..., examples=[1])
    report_name: str = Field(..., examples=["Startup_Report_5_2026.pdf"])


class ReportListItem(BaseModel):
    """Stored report metadata displayed in the current user's report list."""

    report_id: int = Field(..., examples=[1])
    startup_id: int = Field(..., examples=[5])
    report_name: Optional[str] = Field(
        default=None,
        examples=["Startup_Report_5_2026.pdf"],
    )
    report_path: Optional[str] = Field(
        default=None,
        examples=["/reports/Startup_Report_5.pdf"],
    )
    generated_on: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp when report metadata was created.",
    )

    model_config = {"from_attributes": True}


class StartupOverview(BaseModel):
    startup_id: int = Field(..., examples=[5])
    startup_name: str = Field(..., examples=["VentureTwin AI"])
    description: str = Field(
        ...,
        examples=["AI-powered digital twin platform for startups."],
    )
    industry: str = Field(..., examples=["Artificial Intelligence"])
    business_type: str = Field(..., examples=["SaaS"])
    stage: str = Field(..., examples=["Seed"])
    target_market: str = Field(..., examples=["B2B startups and SMBs"])


class FinancialSummary(BaseModel):
    initial_budget: Optional[float] = Field(default=None, examples=[50000.0])
    monthly_expenses: Optional[float] = Field(default=None, examples=[8000.0])
    expected_monthly_revenue: Optional[float] = Field(
        default=None,
        examples=[15000.0],
    )
    funding_source: Optional[str] = Field(default=None, examples=["Self Funded"])


class TeamSummary(BaseModel):
    founder: str = Field(..., examples=["Jane Doe"])
    co_founder: Optional[bool] = Field(default=None, examples=[True])
    employees: Optional[int] = Field(default=None, examples=[8])


class BusinessLocationSummary(BaseModel):
    country: str = Field(..., examples=["India"])
    state: str = Field(..., examples=["Karnataka"])
    city: str = Field(..., examples=["Bengaluru"])
    address: Optional[str] = Field(
        default=None,
        examples=["100 MG Road, Bengaluru"],
    )


class LandDetailsSummary(BaseModel):
    has_land: Optional[bool] = Field(default=None, examples=[True])
    land_status: Optional[str] = Field(default=None, examples=["Owned"])
    area: Optional[float] = Field(default=None, examples=[2500.0])
    location: Optional[str] = Field(default=None, examples=["Bengaluru"])
    value: Optional[float] = Field(default=None, examples=[500000.0])
    monthly_rent: Optional[float] = Field(default=None, examples=[0.0])
    expandable: Optional[bool] = Field(default=None, examples=[True])


class PredictionSummary(BaseModel):
    prediction_id: int = Field(..., examples=[12])
    revenue_prediction: float = Field(..., examples=[180000.0])
    profit_prediction: float = Field(..., examples=[84000.0])
    risk_level: str = Field(..., examples=["Medium"])
    health_score: float = Field(..., examples=[90.0])


class ReportSuggestion(BaseModel):
    title: str = Field(..., examples=["Reduce operational expenses"])
    description: str = Field(..., examples=["Review recurring spending."])
    priority: str = Field(..., examples=["HIGH"])
    category: str = Field(..., examples=["Finance"])


class ReportDetailResponse(ReportListItem):
    """The complete, current business report for a stored report record."""

    startup: StartupOverview
    financial: Optional[FinancialSummary] = None
    team: Optional[TeamSummary] = None
    business_location: Optional[BusinessLocationSummary] = None
    land_details: Optional[LandDetailsSummary] = None
    prediction: Optional[PredictionSummary] = None
    ai_suggestions: list[ReportSuggestion] = Field(default_factory=list)

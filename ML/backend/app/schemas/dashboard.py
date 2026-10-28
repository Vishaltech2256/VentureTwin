"""Pydantic schemas for the startup dashboard endpoint.

The dashboard assembles every piece of information about one startup into a
single response. All nested schemas are reused verbatim from their respective
modules — no field definitions are duplicated here.
"""

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.ai_suggestions import AISuggestionResponse
from app.schemas.business_location import BusinessLocationResponse
from app.schemas.financial_information import FinancialInformationResponse
from app.schemas.land_detail import LandDetailsResponse
from app.schemas.prediction import PredictionResponse
from app.schemas.report import ReportListItem
from app.schemas.startup_profile import StartupProfileResponse
from app.schemas.team_information import TeamInformationResponse


class DashboardResponse(BaseModel):
    """Complete startup dashboard — all data for one owned startup in one call.

    Sections that have not been filled in yet are returned as ``null``.
    ``ai_suggestions`` and the ``latest_report`` may be empty / null if no data
    has been generated for this startup.
    """

    startup_profile: StartupProfileResponse = Field(
        ...,
        description="Core startup profile details.",
    )
    financial_information: Optional[FinancialInformationResponse] = Field(
        default=None,
        description="Financial information for the startup, or null if not yet added.",
    )
    team_information: Optional[TeamInformationResponse] = Field(
        default=None,
        description="Team information for the startup, or null if not yet added.",
    )
    business_location: Optional[BusinessLocationResponse] = Field(
        default=None,
        description="Business location details, or null if not yet added.",
    )
    land_details: Optional[LandDetailsResponse] = Field(
        default=None,
        description="Land / facility details, or null if not yet added.",
    )
    prediction: Optional[PredictionResponse] = Field(
        default=None,
        description="Latest prediction for the startup, or null if none generated.",
    )
    ai_suggestions: list[AISuggestionResponse] = Field(
        default_factory=list,
        description="All AI-generated suggestions for the startup, newest first.",
    )
    latest_report: Optional[ReportListItem] = Field(
        default=None,
        description="Metadata of the most recently generated report, or null if none.",
    )

    model_config = {"from_attributes": True}

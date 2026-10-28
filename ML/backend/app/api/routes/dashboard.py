"""Authenticated API endpoint for the startup dashboard.

Returns every piece of information about one startup in a single response.
The startup must belong to the authenticated user; a 403 is returned otherwise.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.services import dashboard_service

router = APIRouter(tags=["Dashboard"])


@router.get(
    "/{startup_id}",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the complete dashboard for a startup",
    description=(
        "Returns every piece of information stored for a single startup in one "
        "response. The startup must belong to the authenticated user.\n\n"
        "**Sections returned:**\n"
        "- `startup_profile` — core profile (always present)\n"
        "- `financial_information` — budget, revenue, expenses, funding source\n"
        "- `team_information` — founder, co-founder, employee count\n"
        "- `business_location` — country, state, city, address\n"
        "- `land_details` — land status, area, value, rent, expandability\n"
        "- `prediction` — latest revenue/profit prediction, risk level, health score\n"
        "- `ai_suggestions` — all generated AI recommendations (newest first)\n"
        "- `latest_report` — metadata of the most recently generated report\n\n"
        "Sections that have not been filled in yet are returned as `null`. "
        "`ai_suggestions` is an empty array when none have been generated."
    ),
    responses={
        200: {
            "description": "Complete startup dashboard",
            "content": {
                "application/json": {
                    "example": {
                        "startup_profile": {
                            "startup_id": 5,
                            "user_id": 1,
                            "startup_name": "VentureTwin AI",
                            "startup_description": "AI-powered digital twin for startups.",
                            "business_type": "SaaS",
                            "industry": "Artificial Intelligence",
                            "startup_stage": "Seed",
                            "target_market": "B2B Startups and SMBs",
                            "initial_budget": 50000.0,
                            "monthly_expenses": 8000.0,
                            "expected_monthly_revenue": 15000.0,
                            "funding_source": "Self Funded",
                            "founder_name": "Jane Doe",
                            "has_cofounder": True,
                            "number_of_employees": 8,
                            "country": "India",
                            "state": "Karnataka",
                            "city": "Bengaluru",
                            "business_address": "100 MG Road, Bengaluru",
                            "has_land": True,
                            "land_status": "Owned",
                            "land_area_sqft": 2500.0,
                            "land_location": "Bengaluru",
                            "land_value": 500000.0,
                            "monthly_rent": None,
                            "expandable": True,
                            "created_at": "2026-07-18T05:00:00",
                            "updated_at": "2026-07-18T10:00:00",
                        },
                        "financial_information": {
                            "financial_id": 3,
                            "startup_id": 5,
                            "initial_budget": 50000.0,
                            "monthly_expenses": 8000.0,
                            "expected_monthly_revenue": 15000.0,
                            "funding_source": "Self Funded",
                            "created_at": "2026-07-18T05:10:00",
                        },
                        "team_information": {
                            "team_id": 2,
                            "startup_id": 5,
                            "founder_name": "Jane Doe",
                            "co_founder_name": "John Smith",
                            "number_of_employees": 8,
                            "created_at": "2026-07-18T05:15:00",
                        },
                        "business_location": {
                            "location_id": 4,
                            "startup_id": 5,
                            "country": "India",
                            "state": "Karnataka",
                            "city": "Bengaluru",
                            "business_address": "100 MG Road, Bengaluru",
                            "created_at": "2026-07-18T05:20:00",
                        },
                        "land_details": {
                            "land_id": 1,
                            "startup_id": 5,
                            "has_land": True,
                            "land_status": "Owned",
                            "land_area_sqft": 2500,
                            "land_location": "Bengaluru",
                            "land_value": 500000.0,
                            "monthly_rent": None,
                            "expandable": True,
                            "created_at": "2026-07-18T05:25:00",
                        },
                        "prediction": {
                            "prediction_id": 12,
                            "startup_id": 5,
                            "revenue_prediction": 180000.0,
                            "profit_prediction": 84000.0,
                            "risk_level": "Low",
                            "health_score": 90.0,
                            "created_at": "2026-07-18T10:00:00",
                        },
                        "ai_suggestions": [
                            {
                                "suggestion_id": 7,
                                "startup_id": 5,
                                "prediction_id": 12,
                                "title": "Explore investor funding",
                                "description": (
                                    "Prepare an investment case and explore suitable "
                                    "investor funding options to support the next stage "
                                    "of growth."
                                ),
                                "priority": "MEDIUM",
                                "category": "Investment",
                                "created_at": "2026-07-18T10:05:00",
                            }
                        ],
                        "latest_report": {
                            "report_id": 1,
                            "startup_id": 5,
                            "report_name": "Startup_Report_5_2026.pdf",
                            "report_path": "/reports/Startup_Report_5.pdf",
                            "generated_on": "2026-07-18T10:30:00",
                        },
                    }
                }
            },
        },
        401: {"description": "Missing or invalid JWT token"},
        403: {"description": "Startup belongs to another user"},
        404: {"description": "Startup profile not found"},
        500: {"description": "Internal server error"},
    },
)
def get_dashboard(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the complete dashboard for one owned startup."""
    return dashboard_service.get_dashboard(
        db=db,
        startup_id=startup_id,
        user_id=current_user.id,
    )

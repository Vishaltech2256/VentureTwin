from fastapi import APIRouter
from app.api.routes import (
    auth,
    startup_profile,
    financial_information,
    team_information,
    business_location,
    land_details,
    predictions,
    ai_suggestions,
    reports,
    dashboard,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(startup_profile.router, prefix="/startup-profile")
api_router.include_router(financial_information.router, prefix="/financial-information")
api_router.include_router(team_information.router, prefix="/team-information")
api_router.include_router(business_location.router, prefix="/business-location")
api_router.include_router(land_details.router, prefix="/land-details")
api_router.include_router(predictions.router, prefix="/predictions")
api_router.include_router(ai_suggestions.router, prefix="/ai-suggestions")
api_router.include_router(reports.router, prefix="/reports")
api_router.include_router(dashboard.router, prefix="/dashboard")


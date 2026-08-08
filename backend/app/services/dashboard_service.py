"""Service layer for the startup dashboard endpoint.

Aggregates every piece of data related to a single startup into one dictionary
that is returned by the dashboard route. All queries use SQLAlchemy ORM —
no raw SQL. Ownership is verified before any data is fetched.
"""

import logging
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.ai_suggestion import AISuggestion
from app.models.prediction import Prediction
from app.models.report import Report
from app.models.startup_profile import StartupProfile

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _verify_ownership(db: Session, startup_id: int, user_id: int) -> StartupProfile:
    """Fetch a startup and confirm it belongs to the requesting user.

    Raises:
        404 – startup not found.
        403 – startup is owned by a different user.
    """
    startup = (
        db.query(StartupProfile)
        .filter(StartupProfile.startup_id == startup_id)
        .first()
    )
    if startup is None:
        logger.warning(
            "Dashboard: startup_id=%s not found (requested by user_id=%s)",
            startup_id,
            user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found.",
        )
    if startup.user_id != user_id:
        logger.warning(
            "Dashboard: user_id=%s attempted to access startup_id=%s owned by user_id=%s",
            user_id,
            startup_id,
            startup.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this startup profile.",
        )
    return startup


def _get_latest_prediction(db: Session, startup_id: int) -> Prediction | None:
    """Return the most recent prediction for a startup, or None."""
    return (
        db.query(Prediction)
        .filter(Prediction.startup_id == startup_id)
        .order_by(Prediction.created_at.desc(), Prediction.prediction_id.desc())
        .first()
    )


def _get_ai_suggestions(db: Session, startup_id: int) -> list[AISuggestion]:
    """Return all AI suggestions for a startup, newest first."""
    return (
        db.query(AISuggestion)
        .filter(AISuggestion.startup_id == startup_id)
        .order_by(AISuggestion.created_at.desc(), AISuggestion.suggestion_id.desc())
        .all()
    )


def _get_latest_report(db: Session, startup_id: int) -> Report | None:
    """Return the most recently generated report metadata for a startup, or None."""
    return (
        db.query(Report)
        .filter(Report.startup_id == startup_id)
        .order_by(Report.generated_on.desc(), Report.report_id.desc())
        .first()
    )


# ---------------------------------------------------------------------------
# Public service function
# ---------------------------------------------------------------------------


def get_dashboard(db: Session, startup_id: int, user_id: int) -> dict[str, Any]:
    """Assemble and return the complete dashboard for one owned startup.

    Steps:
      1. Verify the startup exists and belongs to the requesting user (403/404).
      2. Collect all related data via the ORM relationships and separate queries.
      3. Return a structured dictionary ready for Pydantic serialisation.

    Raises:
        403 – startup belongs to a different user.
        404 – startup profile not found.
        500 – unexpected database error.
    """
    try:
        startup = _verify_ownership(db, startup_id, user_id)

        # Related records accessed via SQLAlchemy eager-loaded relationships
        financial = startup.financial_info
        team = startup.team_info
        location = startup.location
        land = startup.land_detail

        # Records that require separate queries (not joined to StartupProfile)
        prediction = _get_latest_prediction(db, startup_id)
        suggestions = _get_ai_suggestions(db, startup_id)
        latest_report = _get_latest_report(db, startup_id)

        logger.info(
            "Dashboard assembled for startup_id=%s by user_id=%s",
            startup_id,
            user_id,
        )

        return {
            "startup_profile": startup,
            "financial_information": financial,
            "team_information": team,
            "business_location": location,
            "land_details": land,
            "prediction": prediction,
            "ai_suggestions": suggestions,
            "latest_report": latest_report,
        }

    except HTTPException:
        # Re-raise expected 403 / 404 without wrapping them
        raise
    except SQLAlchemyError:
        logger.exception(
            "Dashboard: database error for startup_id=%s user_id=%s",
            startup_id,
            user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while loading the dashboard.",
        )

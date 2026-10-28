"""Business rules and CRUD operations for AI-generated suggestions."""

import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.ai_suggestion import AISuggestion
from app.models.prediction import Prediction
from app.models.startup_profile import StartupProfile
from app.schemas.ai_suggestions import SuggestionCategory, SuggestionPriority

logger = logging.getLogger(__name__)


def _get_owned_startup(db: Session, startup_id: int, user_id: int) -> StartupProfile:
    """Get a startup and ensure that it belongs to the authenticated user."""
    startup = (
        db.query(StartupProfile)
        .filter(StartupProfile.startup_id == startup_id)
        .first()
    )
    if startup is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found",
        )
    if startup.user_id != user_id:
        logger.warning(
            "User %s attempted to access startup %s owned by user %s",
            user_id,
            startup_id,
            startup.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this startup profile",
        )
    return startup


def _get_latest_prediction(db: Session, startup_id: int) -> Prediction:
    """Return the newest prediction available for a startup."""
    prediction = (
        db.query(Prediction)
        .filter(Prediction.startup_id == startup_id)
        .order_by(Prediction.created_at.desc(), Prediction.prediction_id.desc())
        .first()
    )
    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No prediction is available for this startup. "
                "Generate a prediction before generating AI suggestions."
            ),
        )
    return prediction


def _suggestion_rules(
    startup: StartupProfile, prediction: Prediction
) -> list[dict[str, str]]:
    """Evaluate the defined recommendation rules against the latest prediction."""
    suggestions: list[dict[str, str]] = []

    if (prediction.risk_level or "").strip().upper() == "HIGH":
        suggestions.append(
            {
                "title": "Reduce operational expenses",
                "description": (
                    "Review recurring spending, reduce non-essential costs, "
                    "and improve cash flow."
                ),
                "priority": SuggestionPriority.HIGH.value,
                "category": SuggestionCategory.FINANCE.value,
            }
        )

    if float(prediction.health_score) < 50:
        suggestions.append(
            {
                "title": "Improve business sustainability",
                "description": (
                    "Strengthen the operating model, preserve cash, and address "
                    "the factors lowering the startup health score."
                ),
                "priority": SuggestionPriority.HIGH.value,
                "category": SuggestionCategory.OPERATIONS.value,
            }
        )

    # Prediction Engine persists annual projections. Convert them to monthly values
    # before comparing to the startup's monthly expense and profit thresholds.
    monthly_revenue = float(prediction.revenue_prediction) / 12
    monthly_profit = float(prediction.profit_prediction) / 12
    financial_info = startup.financial_info
    monthly_expenses = (
        float(financial_info.monthly_expenses or 0) if financial_info else 0
    )

    if monthly_revenue < monthly_expenses:
        suggestions.append(
            {
                "title": "Increase customer acquisition",
                "description": (
                    "Prioritize customer acquisition campaigns and conversion "
                    "improvements to lift monthly revenue above monthly expenses."
                ),
                "priority": SuggestionPriority.HIGH.value,
                "category": SuggestionCategory.MARKETING.value,
            }
        )

    if monthly_profit > 100_000:
        suggestions.append(
            {
                "title": "Consider expanding operations",
                "description": (
                    "Use the strong monthly profit position to evaluate a measured "
                    "expansion of capacity, markets, or product offerings."
                ),
                "priority": SuggestionPriority.LOW.value,
                "category": SuggestionCategory.GROWTH.value,
            }
        )

    funding_source = (
        (financial_info.funding_source or "").strip().casefold()
        if financial_info
        else ""
    )
    if funding_source == "self funded":
        suggestions.append(
            {
                "title": "Explore investor funding",
                "description": (
                    "Prepare an investment case and explore suitable investor funding "
                    "options to support the next stage of growth."
                ),
                "priority": SuggestionPriority.MEDIUM.value,
                "category": SuggestionCategory.INVESTMENT.value,
            }
        )

    return suggestions


def generate_suggestions(
    db: Session, startup_id: int, user_id: int
) -> tuple[Prediction, list[AISuggestion]]:
    """Generate idempotent suggestions for the latest prediction and persist them."""
    startup = _get_owned_startup(db, startup_id, user_id)
    prediction = _get_latest_prediction(db, startup_id)
    rule_results = _suggestion_rules(startup, prediction)

    try:
        # Regeneration is idempotent for a prediction: it refreshes stale output
        # without accumulating identical recommendations for the user.
        (
            db.query(AISuggestion)
            .filter(AISuggestion.prediction_id == prediction.prediction_id)
            .delete(synchronize_session=False)
        )

        suggestions = [
            AISuggestion(
                startup_id=startup_id,
                prediction_id=prediction.prediction_id,
                **rule_result,
            )
            for rule_result in rule_results
        ]
        db.add_all(suggestions)
        db.commit()

        for suggestion in suggestions:
            db.refresh(suggestion)

        logger.info(
            "Generated %s AI suggestion(s) for startup %s from prediction %s",
            len(suggestions),
            startup_id,
            prediction.prediction_id,
        )
        return prediction, suggestions
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "Failed to generate AI suggestions for startup %s", startup_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating AI suggestions.",
        )


def get_suggestions(
    db: Session, startup_id: int, user_id: int
) -> list[AISuggestion]:
    """Return all suggestions for an owned startup, newest first."""
    _get_owned_startup(db, startup_id, user_id)
    return (
        db.query(AISuggestion)
        .filter(AISuggestion.startup_id == startup_id)
        .order_by(AISuggestion.created_at.desc(), AISuggestion.suggestion_id.desc())
        .all()
    )


def get_suggestion_by_id(
    db: Session, suggestion_id: int, user_id: int
) -> AISuggestion:
    """Return one suggestion after verifying ownership through its startup."""
    suggestion = (
        db.query(AISuggestion)
        .filter(AISuggestion.suggestion_id == suggestion_id)
        .first()
    )
    if suggestion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI suggestion not found",
        )
    _get_owned_startup(db, suggestion.startup_id, user_id)
    return suggestion


def delete_suggestion(db: Session, suggestion_id: int, user_id: int) -> None:
    """Delete one suggestion after verifying ownership."""
    suggestion = get_suggestion_by_id(db, suggestion_id, user_id)
    try:
        db.delete(suggestion)
        db.commit()
        logger.info("Deleted AI suggestion %s", suggestion_id)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to delete AI suggestion %s", suggestion_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the AI suggestion.",
        )

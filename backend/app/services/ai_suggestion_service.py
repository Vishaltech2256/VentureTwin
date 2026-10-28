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
    """Evaluate the defined recommendation rules against the startup and its latest prediction."""
    suggestions: list[dict[str, str]] = []

    from app.services.prediction_service import _attach_ml_fields
    _attach_ml_fields(prediction, startup)

    financial_info = startup.financial_info
    monthly_expenses = (
        float(financial_info.monthly_expenses or 0) if financial_info else 0.0
    )
    monthly_revenue = float(prediction.revenue_prediction or 0) / 12
    annual_profit = float(prediction.profit_prediction or 0)
    monthly_profit = annual_profit / 12
    health_score = float(prediction.health_score or 0)
    risk_level = (prediction.risk_level or "").strip().upper()

    # 1. Machine Learning Relative Success Likelihood Evaluation
    rel_likelihood = getattr(prediction, "relative_success_likelihood", None)
    rel_perc = getattr(prediction, "relative_likelihood_percentage", None) or (
        f"{rel_likelihood * 100:.1f}%" if rel_likelihood is not None else None
    )
    rel_class = getattr(prediction, "relative_classification", "Moderate/Low Relative Likelihood")

    if rel_likelihood is not None:
        if rel_likelihood < 0.35:
            suggestions.append(
                {
                    "title": "Strengthen venture capitalization and cohort positioning",
                    "description": (
                        f"The ML model evaluates this startup at a Relative Success Likelihood of {rel_perc} "
                        f"({rel_class}) against historical resolved venture cohorts. Consider extending runway "
                        f"through strategic angel commitments and optimizing unit economics to improve relative venture standing."
                    ),
                    "priority": SuggestionPriority.HIGH.value,
                    "category": SuggestionCategory.INVESTMENT.value,
                }
            )
        elif rel_likelihood < 0.50:
            suggestions.append(
                {
                    "title": "Enhance product-market validation to elevate cohort ranking",
                    "description": (
                        f"With a Relative Success Likelihood of {rel_perc} ({rel_class}), prioritize customer "
                        f"discovery and iterative feedback loops to demonstrate early traction and accelerate growth."
                    ),
                    "priority": SuggestionPriority.MEDIUM.value,
                    "category": SuggestionCategory.GROWTH.value,
                }
            )
        else:
            suggestions.append(
                {
                    "title": "Capitalize on favorable cohort positioning",
                    "description": (
                        f"With a Relative Success Likelihood of {rel_perc} ({rel_class}), the venture is positioned "
                        f"competitively against historical peers. Accelerate go-to-market channels."
                    ),
                    "priority": SuggestionPriority.LOW.value,
                    "category": SuggestionCategory.GROWTH.value,
                }
            )

    # 2. Risk Level and Profitability Classification
    if risk_level == "HIGH":
        suggestions.append(
            {
                "title": "Reduce operational expenses",
                "description": (
                    "Review recurring spending, eliminate non-essential costs, "
                    "and improve cash flow to reach operational break-even."
                ),
                "priority": SuggestionPriority.HIGH.value,
                "category": SuggestionCategory.FINANCE.value,
            }
        )
    elif risk_level == "MEDIUM":
        suggestions.append(
            {
                "title": "Strengthen operating profit margins",
                "description": (
                    f"Projected annual profit is ${annual_profit:,.2f} (${monthly_profit:,.2f}/month), placing the "
                    f"startup in the Medium risk tier. Refine pricing structures and control variable expenses "
                    f"to elevate profitability toward the Low risk threshold ($100,000+ annual profit)."
                ),
                "priority": SuggestionPriority.MEDIUM.value,
                "category": SuggestionCategory.FINANCE.value,
            }
        )
    elif risk_level == "LOW":
        suggestions.append(
            {
                "title": "Reinvest healthy margins into scalable growth",
                "description": (
                    f"Annual projected profit is solid at ${annual_profit:,.2f}. Reinvest operating surplus "
                    f"into high-ROI customer acquisition and product development."
                ),
                "priority": SuggestionPriority.LOW.value,
                "category": SuggestionCategory.FINANCE.value,
            }
        )

    # 3. Health Score and Operational Foundation
    if health_score < 50:
        suggestions.append(
            {
                "title": "Improve business sustainability",
                "description": (
                    "Strengthen the operating model, preserve cash reserves, and address "
                    "the key structural factors lowering the startup health score."
                ),
                "priority": SuggestionPriority.HIGH.value,
                "category": SuggestionCategory.OPERATIONS.value,
            }
        )
    elif health_score >= 80:
        suggestions.append(
            {
                "title": "Leverage strong operational foundation",
                "description": (
                    f"Startup health score is strong at {health_score:.0f}/100. Leverage this structural stability "
                    f"when negotiating strategic partnerships and preparing investor presentations."
                ),
                "priority": SuggestionPriority.LOW.value,
                "category": SuggestionCategory.OPERATIONS.value,
            }
        )

    # 4. Revenue vs Expenses Unit Economics
    if monthly_revenue < monthly_expenses:
        suggestions.append(
            {
                "title": "Increase customer acquisition velocity",
                "description": (
                    "Prioritize targeted customer acquisition campaigns and conversion improvements "
                    "to lift monthly revenue above current monthly burn."
                ),
                "priority": SuggestionPriority.HIGH.value,
                "category": SuggestionCategory.MARKETING.value,
            }
        )
    elif monthly_revenue >= monthly_expenses and monthly_revenue > 0:
        suggestions.append(
            {
                "title": "Accelerate customer retention and expansion",
                "description": (
                    f"Target monthly revenue (${monthly_revenue:,.2f}) covers monthly operating expenses (${monthly_expenses:,.2f}). "
                    f"Focus on customer retention, expansion revenue, and increasing average contract value."
                ),
                "priority": SuggestionPriority.MEDIUM.value,
                "category": SuggestionCategory.MARKETING.value,
            }
        )

    # 5. Funding Source Strategy
    funding_source = (
        (financial_info.funding_source or "").strip().casefold()
        if financial_info
        else ""
    )
    if funding_source == "self funded":
        suggestions.append(
            {
                "title": "Explore external investor funding",
                "description": (
                    "Prepare an investment deck and explore suitable angel or venture capital "
                    "options to accelerate market traction without exhausting personal capital."
                ),
                "priority": SuggestionPriority.MEDIUM.value,
                "category": SuggestionCategory.INVESTMENT.value,
            }
        )
    elif funding_source in {"angel round", "angel", "bootstrapped"}:
        suggestions.append(
            {
                "title": "Define milestones for institutional funding",
                "description": (
                    f"Currently backed by '{financial_info.funding_source}'. Establish clear product and revenue "
                    f"milestones needed to prepare for institutional seed or Series A venture capital."
                ),
                "priority": SuggestionPriority.MEDIUM.value,
                "category": SuggestionCategory.INVESTMENT.value,
            }
        )

    # 6. Team & Scaling
    team_info = startup.team_info
    employee_count = (
        team_info.number_of_employees
        if team_info and team_info.number_of_employees is not None
        else 0
    )
    if employee_count <= 2:
        suggestions.append(
            {
                "title": "Plan strategic core team hires",
                "description": (
                    "With a compact founding team, identify critical skill gaps in technical development or "
                    "sales and plan key strategic hires as operational volume grows."
                ),
                "priority": SuggestionPriority.MEDIUM.value,
                "category": SuggestionCategory.HIRING.value,
            }
        )

    return suggestions



def generate_suggestions(
    db: Session, startup_id: int, user_id: int
) -> tuple[Prediction, list[AISuggestion]]:
    """Generate idempotent suggestions for the latest prediction and persist them."""
    startup = _get_owned_startup(db, startup_id, user_id)
    prediction = _get_latest_prediction(db, startup_id)
    logger.info(
        "Evaluating AI suggestion rules for startup_id=%s, prediction_id=%s (risk=%s, health=%s, rev=%s, profit=%s, stage=%s)",
        startup_id,
        prediction.prediction_id,
        prediction.risk_level,
        prediction.health_score,
        prediction.revenue_prediction,
        prediction.profit_prediction,
        startup.startup_stage,
    )
    rule_results = _suggestion_rules(startup, prediction)
    if not rule_results:
        logger.warning(
            "0 AI suggestion rules matched for startup_id=%s, prediction_id=%s",
            startup_id,
            prediction.prediction_id,
        )


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

# app/services/prediction_service.py

import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.startup_profile import StartupProfile
from app.models.prediction import Prediction
from venturetwin_ml import predict_startup, simulate_whatif

logger = logging.getLogger(__name__)



# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_startup_and_verify_ownership(
    db: Session, startup_id: int, user_id: int
) -> StartupProfile:
    """
    Fetch the startup profile and assert it belongs to the requesting user.

    Raises:
        404 — Startup not found.
        403 — Startup belongs to a different user.
    """
    startup = (
        db.query(StartupProfile)
        .filter(StartupProfile.startup_id == startup_id)
        .first()
    )
    if not startup:
        logger.warning(f"Startup not found: startup_id={startup_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found",
        )
    if startup.user_id != user_id:
        logger.warning(
            f"Forbidden: user_id={user_id} attempted to access startup_id={startup_id} "
            f"owned by user_id={startup.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this startup profile",
        )
    return startup


def _get_prediction_record(db: Session, prediction_id: int) -> Prediction:
    """
    Fetch a Prediction record by its primary key or raise 404.
    """
    record = (
        db.query(Prediction)
        .filter(Prediction.prediction_id == prediction_id)
        .first()
    )
    if not record:
        logger.warning(f"Prediction not found: prediction_id={prediction_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )
    return record


# ---------------------------------------------------------------------------
# Calculation engine
# ---------------------------------------------------------------------------

def _calculate_revenue_prediction(startup: StartupProfile) -> float:
    """Annual revenue = expected_monthly_revenue × 12."""
    monthly_revenue = float(startup.financial_info.expected_monthly_revenue or 0)
    return round(monthly_revenue * 12, 2)


def _calculate_profit_prediction(
    startup: StartupProfile, revenue_prediction: float
) -> float:
    """Annual profit = revenue_prediction − (monthly_expenses × 12)."""
    annual_expenses = float(startup.financial_info.monthly_expenses or 0) * 12
    return round(revenue_prediction - annual_expenses, 2)


def _calculate_risk_level(profit_prediction: float) -> str:
    """
    Risk classification based on annual profit:
      - profit <= 0        → "High"
      - 0 < profit < 100000 → "Medium"
      - profit >= 100000   → "Low"
    """
    if profit_prediction <= 0:
        return "High"
    elif profit_prediction < 100_000:
        return "Medium"
    else:
        return "Low"


def _calculate_health_score(
    startup: StartupProfile, revenue_prediction: float
) -> float:
    """
    Composite health score starting at 50, with up to 5 bonus criteria (+10 each).

    Criteria:
      +10 — funding_source is "Investor" or "Angel Round"
      +10 — number_of_employees > 5
      +10 — startup_stage is "Seed" or "Growth"
      +10 — has_land is True
      +10 — revenue_prediction > (monthly_expenses × 12)

    Score is clamped between 0 and 100.
    """
    score = 50.0

    # Funding source bonus
    funding_source = (startup.financial_info.funding_source or "").strip().lower()
    if funding_source in {"investor", "angel round"}:
        score += 10

    # Employee count bonus
    employee_count = startup.team_info.number_of_employees if startup.team_info is not None else None
    if employee_count is not None and employee_count > 5:
        score += 10

    # Startup stage bonus
    startup_stage = (startup.startup_stage or "").strip().lower()
    if startup_stage in {"seed", "growth"}:
        score += 10

    # Land ownership bonus
    has_land = startup.land_detail.has_land if startup.land_detail is not None else None
    if has_land is True:
        score += 10

    # Revenue vs expenses bonus
    annual_expenses = float(startup.financial_info.monthly_expenses or 0) * 12
    if revenue_prediction > annual_expenses:
        score += 10

    # Clamp between 0 and 100
    return round(max(0.0, min(100.0, score)), 2)


def _validate_financial_data(startup: StartupProfile) -> None:
    """
    Ensure all data required for calculation is present.

    Raises:
        400 — If financial information is incomplete.
    """
    if not startup.financial_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Financial information is missing for this startup. "
                "Please add financial data before generating a prediction."
            ),
        )
    if startup.financial_info.expected_monthly_revenue is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expected_monthly_revenue is required to generate a prediction.",
        )
    if startup.financial_info.monthly_expenses is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="monthly_expenses is required to generate a prediction.",
        )


# ---------------------------------------------------------------------------
# ML input adapter & dynamic attachment helpers
# ---------------------------------------------------------------------------

def _build_ml_input(startup: StartupProfile) -> dict:
    """
    Constructs the input dictionary for venturetwin_ml server-side from
    existing database models, eliminating redundant frontend submissions.
    """
    financial = startup.financial_info
    team = startup.team_info
    location = startup.location
    land = startup.land_detail

    initial_budget = float(financial.initial_budget or 0.0) if financial else 0.0
    monthly_expenses = float(financial.monthly_expenses or 0.0) if financial else 0.0
    expected_monthly_rev = float(financial.expected_monthly_revenue or 0.0) if financial else 0.0
    funding_source = financial.funding_source if financial else None

    num_employees = (
        team.number_of_employees
        if (team is not None and team.number_of_employees is not None)
        else 2
    )

    country = location.country if location else None
    state = location.state if location else None

    has_land = land.has_land if (land is not None and land.has_land is not None) else False

    return {
        "business_type": startup.business_type or "Software",
        "budget": initial_budget,
        "currency": "USD",
        "monthly_expenses": monthly_expenses,
        "expected_monthly_revenue": expected_monthly_rev,
        "num_employees": num_employees,
        "country": country,
        "state": state,
        "startup_stage": startup.startup_stage or "Seed",
        "funding_source": funding_source,
        "has_land": has_land,
    }


def _attach_ml_fields(
    record: Prediction, startup: Optional[StartupProfile] = None
) -> None:
    """
    Dynamically attaches ML evaluation attributes onto a Prediction instance
    for response serialization, preserving database schema compatibility.
    """
    if getattr(record, "relative_success_likelihood", None) is not None:
        return

    try:
        target_startup = startup or record.startup
        if target_startup and target_startup.financial_info:
            ml_input = _build_ml_input(target_startup)
            ml_result = predict_startup(ml_input)
            record.relative_success_likelihood = ml_result.get("relative_success_likelihood")
            record.relative_likelihood_percentage = ml_result.get("relative_likelihood_percentage")
            record.relative_classification = ml_result.get("relative_classification")
            record.ml_model_evaluation = ml_result.get("ml_model_evaluation")
            record.warnings = ml_result.get("warnings")
    except Exception as e:
        logger.warning(
            f"Could not dynamically evaluate ML likelihood for prediction_id={record.prediction_id}: {e}"
        )


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------

def generate_prediction(
    db: Session,
    startup_id: int,
    user_id: int,
) -> Prediction:
    """
    Generate a new prediction for the given startup and persist it to the database.

    Every call creates a NEW record — previous predictions are never overwritten.

    Steps:
      1. Verify startup exists and belongs to the requesting user.
      2. Validate that required financial data is present.
      3. Construct ML input dictionary server-side from database models.
      4. Call venturetwin_ml.predict_startup() for ML evaluation.
      5. Extract operational formula estimates for backward-compatible fields.
      6. Persist the record and attach dynamic ML fields.
      7. Return the record.

    Raises:
        400 — Financial data missing or incomplete.
        403 — Startup belongs to a different user.
        404 — Startup not found.
        500 — ML inference or database error.
        503 — ML model artifacts unavailable.
    """
    logger.info(f"Generating prediction for startup_id={startup_id} by user_id={user_id}")

    startup = _get_startup_and_verify_ownership(db, startup_id, user_id)
    _validate_financial_data(startup)

    # Build ML input dictionary server-side from existing records
    ml_input = _build_ml_input(startup)

    # Call ML service with strict error handling and NO fake fallbacks
    try:
        ml_result = predict_startup(ml_input)
    except FileNotFoundError as e:
        logger.error(f"ML model artifacts missing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction model artifacts are currently unavailable.",
        )
    except Exception as e:
        logger.error(f"ML prediction inference error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while evaluating the machine learning prediction.",
        )

    # Extract operational formula estimates (strictly deterministic, NOT ML predictions)
    operational = ml_result["operational_formula_estimates"]
    revenue_prediction = operational["estimated_annual_revenue"]
    profit_prediction = operational["estimated_annual_profit"]
    risk_level = operational["formula_risk_level"]
    health_score = operational["formula_health_score"]

    try:
        # Manually compute next primary key (follows project convention)
        max_id = db.query(func.max(Prediction.prediction_id)).scalar() or 0
        next_id = max_id + 1

        record = Prediction(
            prediction_id=next_id,
            startup_id=startup_id,
            revenue_prediction=revenue_prediction,
            profit_prediction=profit_prediction,
            risk_level=risk_level,
            health_score=health_score,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # Attach real ML fields dynamically onto the returned record
        record.relative_success_likelihood = ml_result.get("relative_success_likelihood")
        record.relative_likelihood_percentage = ml_result.get("relative_likelihood_percentage")
        record.relative_classification = ml_result.get("relative_classification")
        record.ml_model_evaluation = ml_result.get("ml_model_evaluation")
        record.warnings = ml_result.get("warnings")

        logger.info(
            f"Prediction created: prediction_id={record.prediction_id} "
            f"for startup_id={startup_id} | ML likelihood={record.relative_success_likelihood} | "
            f"risk={risk_level} | health={health_score}"
        )
        return record
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save prediction for startup_id={startup_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the prediction record.",
        )


def get_predictions(db: Session, user_id: int) -> list[Prediction]:
    """
    Return all predictions belonging to the authenticated user
    (i.e., all prediction records whose parent startup is owned by this user).
    """
    logger.info(f"Fetching all predictions for user_id={user_id}")
    records = (
        db.query(Prediction)
        .join(StartupProfile, Prediction.startup_id == StartupProfile.startup_id)
        .filter(StartupProfile.user_id == user_id)
        .order_by(Prediction.created_at.desc())
        .all()
    )
    for record in records:
        _attach_ml_fields(record)
    return records


def get_prediction_by_id(
    db: Session, prediction_id: int, user_id: int
) -> Prediction:
    """
    Return a single prediction by its primary key.

    Raises:
        403 — Prediction belongs to a startup owned by a different user.
        404 — Prediction not found.
    """
    logger.info(f"Fetching prediction_id={prediction_id} for user_id={user_id}")
    record = _get_prediction_record(db, prediction_id)

    # Verify ownership via the parent startup
    startup = _get_startup_and_verify_ownership(db, record.startup_id, user_id)
    _attach_ml_fields(record, startup)
    return record


def simulate_whatif_scenario(
    db: Session, startup_id: int, user_id: int, changes: dict
) -> dict:
    """
    Evaluates a what-if hypothetical scenario for an existing startup profile
    using venturetwin_ml.simulate_whatif.

    Only changes to budget, business_type, and location impact the ML Relative Success Likelihood.
    Changes to operational values update deterministic financial formula estimates.
    """
    startup = _get_startup_and_verify_ownership(db, startup_id, user_id)
    _validate_financial_data(startup)

    base_input = _build_ml_input(startup)
    try:
        return simulate_whatif(base_input=base_input, changes=changes)
    except FileNotFoundError as e:
        logger.error(f"ML model artifacts missing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction model artifacts are currently unavailable.",
        )
    except Exception as e:
        logger.error(f"ML simulation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while running what-if simulation.",
        )



def delete_prediction(
    db: Session, prediction_id: int, user_id: int
) -> None:
    """
    Permanently delete a prediction record.

    Raises:
        403 — Prediction belongs to a startup owned by a different user.
        404 — Prediction not found.
        500 — Database error.
    """
    logger.info(f"Deleting prediction_id={prediction_id} by user_id={user_id}")
    record = _get_prediction_record(db, prediction_id)

    # Verify ownership via the parent startup
    _get_startup_and_verify_ownership(db, record.startup_id, user_id)

    try:
        db.delete(record)
        db.commit()
        logger.info(f"Prediction deleted: prediction_id={prediction_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete prediction_id={prediction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the prediction.",
        )

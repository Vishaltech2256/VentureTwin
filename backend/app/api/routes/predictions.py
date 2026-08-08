# app/api/routes/predictions.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.prediction import PredictionResponse
from app.services import prediction_service

router = APIRouter(tags=["Prediction Engine"])


@router.post(
    "/generate/{startup_id}",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a prediction for a startup",
    description=(
        "Runs the prediction engine against all data linked to the specified startup and "
        "saves the result as a new record in the database.\n\n"
        "**Every call creates a brand-new prediction record** — previous predictions are "
        "never overwritten, giving you a full history of all runs.\n\n"
        "**Calculation formulas:**\n"
        "- **Revenue Prediction** = `expected_monthly_revenue × 12`\n"
        "- **Profit Prediction** = `revenue_prediction − (monthly_expenses × 12)`\n"
        "- **Risk Level:**\n"
        "  - `High` → profit ≤ 0\n"
        "  - `Medium` → 0 < profit < 100,000\n"
        "  - `Low` → profit ≥ 100,000\n"
        "- **Health Score** (0–100, base 50):\n"
        "  - +10 if funding source is *Investor* or *Angel Round*\n"
        "  - +10 if employee count > 5\n"
        "  - +10 if startup stage is *Seed* or *Growth*\n"
        "  - +10 if `has_land = true`\n"
        "  - +10 if revenue prediction > annual expenses\n\n"
        "**Prerequisites:** The startup must have **Financial Information** and "
        "**Team Information** records.\n\n"
        "**Errors:**\n"
        "- `400` — Financial data missing or incomplete\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — Startup belongs to a different user\n"
        "- `404` — Startup profile not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        201: {
            "description": "Prediction generated and saved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "prediction_id": 1,
                        "startup_id": 5,
                        "revenue_prediction": 180000.00,
                        "profit_prediction": 84000.00,
                        "risk_level": "Medium",
                        "health_score": 90.00,
                        "created_at": "2026-07-17T21:00:00",
                    }
                }
            },
        },
        400: {"description": "Financial data missing or incomplete"},
        401: {"description": "Unauthorized — missing or invalid JWT token"},
        403: {"description": "Forbidden — startup belongs to a different user"},
        404: {"description": "Startup profile not found"},
        500: {"description": "Internal server error"},
    },
)
def generate_prediction(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return prediction_service.generate_prediction(
        db=db, startup_id=startup_id, user_id=current_user.id
    )


@router.get(
    "",
    response_model=List[PredictionResponse],
    status_code=status.HTTP_200_OK,
    summary="List all predictions for the logged-in user",
    description=(
        "Returns all prediction records across **all** startup profiles owned by the "
        "authenticated user, ordered by most recent first.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "List of prediction records (most recent first)"},
        401: {"description": "Unauthorized — missing or invalid JWT token"},
        500: {"description": "Internal server error"},
    },
)
def get_my_predictions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return prediction_service.get_predictions(db=db, user_id=current_user.id)


@router.get(
    "/{prediction_id}",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single prediction by ID",
    description=(
        "Returns the full details of a single prediction record identified by "
        "`prediction_id`.\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the startup linked to this prediction.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — Prediction belongs to a startup owned by a different user\n"
        "- `404` — Prediction not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "Prediction record"},
        401: {"description": "Unauthorized — missing or invalid JWT token"},
        403: {"description": "Forbidden — prediction belongs to a different user"},
        404: {"description": "Prediction not found"},
        500: {"description": "Internal server error"},
    },
)
def get_prediction_by_id(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return prediction_service.get_prediction_by_id(
        db=db, prediction_id=prediction_id, user_id=current_user.id
    )


@router.delete(
    "/{prediction_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete a prediction",
    description=(
        "Permanently deletes the prediction record identified by `prediction_id`.\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the startup linked to this prediction.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — Prediction belongs to a startup owned by a different user\n"
        "- `404` — Prediction not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {
            "description": "Prediction deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Prediction deleted successfully"}
                }
            },
        },
        401: {"description": "Unauthorized — missing or invalid JWT token"},
        403: {"description": "Forbidden — prediction belongs to a different user"},
        404: {"description": "Prediction not found"},
        500: {"description": "Internal server error"},
    },
)
def delete_prediction(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prediction_service.delete_prediction(
        db=db, prediction_id=prediction_id, user_id=current_user.id
    )
    return {"message": "Prediction deleted successfully"}

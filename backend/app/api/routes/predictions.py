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
)
@router.post(
    "/run/{startup_id}",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
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
    "/{startup_id}/latest",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the latest prediction for a startup",
)
def get_latest_prediction(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return prediction_service.get_latest_prediction_for_startup(
        db=db, startup_id=startup_id, user_id=current_user.id
    )


@router.get(
    "/detail/{prediction_id}",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single prediction by ID",
)
def get_prediction_detail(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return prediction_service.get_prediction_by_id(
        db=db, prediction_id=prediction_id, user_id=current_user.id
    )


@router.get(
    "/{startup_id}",
    response_model=List[PredictionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all predictions for a startup",
)
def get_predictions_by_startup(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return prediction_service.get_predictions_for_startup(
        db=db, startup_id=startup_id, user_id=current_user.id
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

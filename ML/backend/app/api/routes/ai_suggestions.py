"""Authenticated API endpoints for AI-generated startup suggestions."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.ai_suggestions import (
    AISuggestionGenerationResponse,
    AISuggestionResponse,
)
from app.services import ai_suggestion_service

router = APIRouter(tags=["AI Suggestions"])


@router.post(
    "/generate/{startup_id}",
    response_model=AISuggestionGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate AI suggestions for a startup",
    description=(
        "Evaluates the most recent prediction owned by the authenticated user and "
        "persists the matching recommendations. Regenerating for the same prediction "
        "replaces its previous recommendations, preventing duplicates.\n\n"
        "The Prediction Engine stores annual revenue and profit projections; this "
        "endpoint derives monthly values before applying the monthly revenue-versus-"
        "expense and monthly-profit rules."
    ),
    responses={
        400: {"description": "No prediction is available for the startup"},
        401: {"description": "Missing or invalid JWT token"},
        403: {"description": "Startup belongs to another user"},
        404: {"description": "Startup profile not found"},
        500: {"description": "Internal server error"},
    },
)
def generate_suggestions(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prediction, suggestions = ai_suggestion_service.generate_suggestions(
        db=db,
        startup_id=startup_id,
        user_id=current_user.id,
    )
    return {
        "startup_id": startup_id,
        "prediction_id": prediction.prediction_id,
        "generated_count": len(suggestions),
        "suggestions": suggestions,
    }


@router.get(
    "/detail/{suggestion_id}",
    response_model=AISuggestionResponse,
    summary="Get one AI suggestion",
    description="Returns one suggestion when its parent startup belongs to the authenticated user.",
    responses={
        401: {"description": "Missing or invalid JWT token"},
        403: {"description": "Suggestion belongs to another user"},
        404: {"description": "AI suggestion not found"},
    },
)
def get_suggestion_detail(
    suggestion_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ai_suggestion_service.get_suggestion_by_id(
        db=db,
        suggestion_id=suggestion_id,
        user_id=current_user.id,
    )


@router.get(
    "/{startup_id}",
    response_model=list[AISuggestionResponse],
    summary="List AI suggestions for a startup",
    description="Returns all generated suggestions for an owned startup, newest first.",
    responses={
        401: {"description": "Missing or invalid JWT token"},
        403: {"description": "Startup belongs to another user"},
        404: {"description": "Startup profile not found"},
    },
)
def get_startup_suggestions(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ai_suggestion_service.get_suggestions(
        db=db,
        startup_id=startup_id,
        user_id=current_user.id,
    )


@router.delete(
    "/{suggestion_id}",
    response_model=dict[str, str],
    summary="Delete one AI suggestion",
    description="Permanently deletes a suggestion owned by the authenticated user.",
    responses={
        401: {"description": "Missing or invalid JWT token"},
        403: {"description": "Suggestion belongs to another user"},
        404: {"description": "AI suggestion not found"},
        500: {"description": "Internal server error"},
    },
)
def delete_suggestion(
    suggestion_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ai_suggestion_service.delete_suggestion(
        db=db,
        suggestion_id=suggestion_id,
        user_id=current_user.id,
    )
    return {"message": "AI suggestion deleted successfully"}

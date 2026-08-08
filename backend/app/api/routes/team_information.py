# app/api/routes/team_information.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.team_information import (
    TeamInformationCreate,
    TeamInformationUpdate,
    TeamInformationResponse,
)
from app.services import team_information_service

router = APIRouter(tags=["Team Information"])


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create team information",
    description=(
        "Creates a new team information record linked to a startup profile.\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the referenced startup.\n"
        "- `founder_name` is required and must be at least 2 characters.\n"
        "- `number_of_employees` must be >= 1.\n"
        "- `co_founder_name` is optional.\n"
        "- Only one team record per startup is allowed. Use **PUT** to update an existing one.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own this startup\n"
        "- `404` — Startup profile not found\n"
        "- `409` — Team information already exists for this startup\n"
        "- `422` — Validation error\n"
        "- `500` — Internal server error"
    ),
    responses={
        201: {"description": "Team information created successfully"},
        400: {"description": "Validation error"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Startup profile not found"},
        409: {"description": "Team information already exists for this startup"},
        500: {"description": "Internal server error"},
    },
)
def create_team_information(
    data: TeamInformationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team_information_service.create_team_information(
        db=db, user_id=current_user.id, data=data
    )
    return {"message": "Team information created successfully"}


@router.get(
    "/{startup_id}",
    response_model=TeamInformationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get team information by startup ID",
    description=(
        "Returns the team information record for the given `startup_id`.\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the referenced startup.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own this startup\n"
        "- `404` — Startup or team information not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "Team information record"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Startup or team information not found"},
        500: {"description": "Internal server error"},
    },
)
def get_team_information(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return team_information_service.get_team_information(
        db=db, startup_id=startup_id, user_id=current_user.id
    )


@router.put(
    "/{team_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update team information",
    description=(
        "Partially updates an existing team information record by `team_id`.\n\n"
        "Only the fields included in the request body are updated (PATCH semantics via PUT).\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the startup linked to this record.\n"
        "- `founder_name` must be at least 2 characters if provided.\n"
        "- `number_of_employees` must be >= 1 if provided.\n\n"
        "**Errors:**\n"
        "- `400` — No fields provided / validation error\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own this startup\n"
        "- `404` — Team information not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "Team information updated successfully"},
        400: {"description": "Validation error or no fields provided"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Team information not found"},
        500: {"description": "Internal server error"},
    },
)
def update_team_information(
    team_id: int,
    data: TeamInformationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team_information_service.update_team_information(
        db=db, team_id=team_id, user_id=current_user.id, data=data
    )
    return {"message": "Team information updated successfully"}


@router.delete(
    "/{team_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete team information",
    description=(
        "Permanently deletes the team information record identified by `team_id`.\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the startup linked to this record.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own this startup\n"
        "- `404` — Team information not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "Team information deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Team information not found"},
        500: {"description": "Internal server error"},
    },
)
def delete_team_information(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team_information_service.delete_team_information(
        db=db, team_id=team_id, user_id=current_user.id
    )
    return {"message": "Team information deleted successfully"}

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.startup_profile import CreateStartupProfile, UpdateStartupProfile, StartupProfileResponse
from app.services import startup_profile_service

router = APIRouter(tags=["Startup Profile"])

@router.post(
    "", 
    response_model=StartupProfileResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new startup profile",
    description="Allows an authenticated user to create a startup profile along with team, financial, location, and land details."
)
def create_profile(
    data: CreateStartupProfile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return startup_profile_service.create_startup_profile(db=db, user_id=current_user.id, data=data)


@router.get(
    "", 
    response_model=List[StartupProfileResponse],
    summary="List all startup profiles of the current user",
    description="Retrieves a list of all startup profiles owned by the logged-in user."
)
def list_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return startup_profile_service.list_user_startup_profiles(db=db, user_id=current_user.id)


@router.get(
    "/{startup_id}", 
    response_model=StartupProfileResponse,
    summary="Get details of a single startup profile",
    description="Retrieves the detailed startup profile. Returns 404 if not found, and 403 if it belongs to another user."
)
def get_profile(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    startup = startup_profile_service.get_startup_profile(db=db, startup_id=startup_id)
    startup_profile_service.check_ownership(startup=startup, user_id=current_user.id)
    return startup


@router.put(
    "/{startup_id}", 
    response_model=StartupProfileResponse,
    summary="Update a startup profile",
    description="Updates the existing startup profile and its linked sub-tables. Enforces ownership and dynamic land rules validation."
)
def update_profile(
    startup_id: int,
    data: UpdateStartupProfile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return startup_profile_service.update_startup_profile(db=db, startup_id=startup_id, user_id=current_user.id, data=data)


@router.delete(
    "/{startup_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a startup profile",
    description="Permanently deletes the startup profile and cascades deletion to all related tables (team, financials, location, land)."
)
def delete_profile(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    startup_profile_service.delete_startup_profile(db=db, startup_id=startup_id, user_id=current_user.id)
    return None

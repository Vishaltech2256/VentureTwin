# app/api/routes/business_location.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.business_location import (
    BusinessLocationCreate,
    BusinessLocationUpdate,
    BusinessLocationResponse,
)
from app.services import business_location_service

router = APIRouter(tags=["Business Location"])


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create business location",
    description=(
        "Creates a new business location record linked to a startup profile.\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the referenced startup.\n"
        "- `country`, `state`, `city`, and `business_address` are required and cannot be blank.\n"
        "- `country`, `state`, and `city` are limited to 100 characters each.\n"
        "- Only one business location per startup is allowed. Use **PUT** to update an existing one.\n\n"
        "**Errors:**\n"
        "- `400` — Validation error\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own the startup\n"
        "- `404` — Startup profile not found\n"
        "- `409` — Business location already exists for this startup\n"
        "- `500` — Internal server error"
    ),
    responses={
        201: {"description": "Business location created successfully"},
        400: {"description": "Validation error"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Startup profile not found"},
        409: {"description": "Business location already exists for this startup"},
        500: {"description": "Internal server error"},
    },
)
def create_business_location(
    data: BusinessLocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    business_location_service.create_business_location(
        db=db, user_id=current_user.id, data=data
    )
    return {"message": "Business location created successfully"}


@router.get(
    "",
    response_model=List[BusinessLocationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all business locations of the current user",
    description=(
        "Returns all business location records belonging to the currently authenticated user.\n\n"
        "This endpoint lists location records across **all** startup profiles owned by the user.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "List of business location records"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"},
    },
)
def get_all_business_locations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return business_location_service.get_business_location(
        db=db, user_id=current_user.id
    )


@router.get(
    "/{location_id}",
    response_model=BusinessLocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get business location by ID",
    description=(
        "Returns a single business location record identified by `location_id`.\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the startup linked to this record.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own this startup\n"
        "- `404` — Business location not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "Business location record"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Business location not found"},
        500: {"description": "Internal server error"},
    },
)
def get_business_location_by_id(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return business_location_service.get_business_location_by_id(
        db=db, location_id=location_id, user_id=current_user.id
    )


@router.put(
    "/{location_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update business location",
    description=(
        "Partially updates an existing business location record.\n\n"
        "Only the fields included in the request body are updated (PATCH semantics via PUT).\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the startup linked to this record.\n"
        "- Updated string fields cannot be set to blank or empty values.\n"
        "- `country`, `state`, and `city` are limited to 100 characters each.\n\n"
        "**Errors:**\n"
        "- `400` — No fields provided / validation error\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own this startup\n"
        "- `404` — Business location not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "Business location updated successfully"},
        400: {"description": "Validation error or no fields provided"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Business location not found"},
        500: {"description": "Internal server error"},
    },
)
def update_business_location(
    location_id: int,
    data: BusinessLocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    business_location_service.update_business_location(
        db=db, location_id=location_id, user_id=current_user.id, data=data
    )
    return {"message": "Business location updated successfully"}


@router.delete(
    "/{location_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete business location",
    description=(
        "Permanently deletes the business location record identified by `location_id`.\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the startup linked to this record.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own this startup\n"
        "- `404` — Business location not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "Business location deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Business location not found"},
        500: {"description": "Internal server error"},
    },
)
def delete_business_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    business_location_service.delete_business_location(
        db=db, location_id=location_id, user_id=current_user.id
    )
    return {"message": "Business location deleted successfully"}

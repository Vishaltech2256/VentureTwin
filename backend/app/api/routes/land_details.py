# app/api/routes/land_details.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.land_detail import (
    LandDetailsCreate,
    LandDetailsUpdate,
    LandDetailsResponse,
)
from app.services import land_detail_service

router = APIRouter(tags=["Land Details"])


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create land details",
    description=(
        "Creates a new land details record linked to a startup profile.\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the referenced startup.\n"
        "- `startup_id` and `land_status` are required.\n"
        "- `land_area_sqft`, `land_value`, and `monthly_rent` must be >= 0 if provided.\n"
        "- `land_status` and `land_location` cannot be blank strings.\n"
        "- Only one land details record per startup is allowed. Use **PUT** to update an existing one.\n\n"
        "**Errors:**\n"
        "- `400` — Validation error\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own the startup\n"
        "- `404` — Startup profile not found\n"
        "- `409` — Land details already exist for this startup\n"
        "- `500` — Internal server error"
    ),
    responses={
        201: {"description": "Land details created successfully"},
        400: {"description": "Validation error"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Startup profile not found"},
        409: {"description": "Land details already exist for this startup"},
        500: {"description": "Internal server error"},
    },
)
def create_land_details(
    data: LandDetailsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    land_detail_service.create_land_details(
        db=db, user_id=current_user.id, data=data
    )
    return {"message": "Land details created successfully"}


@router.get(
    "",
    response_model=List[LandDetailsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all land details for the current user",
    description=(
        "Returns all land details records belonging to the currently authenticated user.\n\n"
        "This endpoint lists records across **all** startup profiles owned by the user.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "List of land details records"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"},
    },
)
def get_all_land_details(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return land_detail_service.get_land_details(
        db=db, user_id=current_user.id
    )


@router.get(
    "/{land_id}",
    response_model=LandDetailsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get land details by ID",
    description=(
        "Returns a single land details record identified by `land_id`.\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the startup linked to this record.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own this startup\n"
        "- `404` — Land details not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "Land details record"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Land details not found"},
        500: {"description": "Internal server error"},
    },
)
def get_land_details_by_id(
    land_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return land_detail_service.get_land_details_by_id(
        db=db, land_id=land_id, user_id=current_user.id
    )


@router.put(
    "/{land_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update land details",
    description=(
        "Partially updates an existing land details record.\n\n"
        "Only the fields included in the request body are updated (PATCH semantics via PUT).\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the startup linked to this record.\n"
        "- `land_status` cannot be set to a blank string.\n"
        "- Numeric fields must be >= 0 if provided.\n\n"
        "**Errors:**\n"
        "- `400` — No fields provided / validation error\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own this startup\n"
        "- `404` — Land details not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "Land details updated successfully"},
        400: {"description": "Validation error or no fields provided"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Land details not found"},
        500: {"description": "Internal server error"},
    },
)
def update_land_details(
    land_id: int,
    data: LandDetailsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    land_detail_service.update_land_details(
        db=db, land_id=land_id, user_id=current_user.id, data=data
    )
    return {"message": "Land details updated successfully"}


@router.delete(
    "/{land_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete land details",
    description=(
        "Permanently deletes the land details record identified by `land_id`.\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the startup linked to this record.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own this startup\n"
        "- `404` — Land details not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "Land details deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Land details not found"},
        500: {"description": "Internal server error"},
    },
)
def delete_land_details(
    land_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    land_detail_service.delete_land_details(
        db=db, land_id=land_id, user_id=current_user.id
    )
    return {"message": "Land details deleted successfully"}

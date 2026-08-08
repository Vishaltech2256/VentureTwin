# app/api/routes/financial_information.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.financial_information import (
    FinancialInformationCreate,
    FinancialInformationUpdate,
    FinancialInformationResponse,
)
from app.services import financial_information_service

router = APIRouter(tags=["Financial Information"])


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create financial information",
    description=(
        "Creates a new financial information record linked to a startup profile.\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the referenced startup.\n"
        "- `initial_budget`, `monthly_expenses`, and `expected_monthly_revenue` must be >= 0.\n"
        "- `funding_source` cannot be empty.\n"
        "- Only one financial record per startup is allowed. Use **PUT** to update an existing one.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own the startup\n"
        "- `404` — Startup profile not found\n"
        "- `409` — Financial information already exists for this startup\n"
        "- `422` — Validation error\n"
        "- `500` — Internal server error"
    ),
    responses={
        201: {"description": "Financial information created successfully"},
        400: {"description": "Validation error"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Startup profile not found"},
        409: {"description": "Financial information already exists for this startup"},
        500: {"description": "Internal server error"},
    },
)
def create_financial_info(
    data: FinancialInformationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    financial_information_service.create_financial_info(
        db=db, user_id=current_user.id, data=data
    )
    return {"message": "Financial information created successfully"}


@router.get(
    "",
    response_model=List[FinancialInformationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current user financial information",
    description=(
        "Returns all financial information records belonging to the currently authenticated user.\n\n"
        "This endpoint lists financial records across **all** startup profiles owned by the user.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "List of financial information records"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"},
    },
)
def get_my_financial_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return financial_information_service.get_user_financial_info(
        db=db, user_id=current_user.id
    )


@router.get(
    "/{financial_id}",
    response_model=FinancialInformationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get financial information by ID",
    description=(
        "Returns a single financial information record identified by `financial_id`.\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the startup linked to this record.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own this startup\n"
        "- `404` — Financial information not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "Financial information record"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Financial information not found"},
        500: {"description": "Internal server error"},
    },
)
def get_financial_info_by_id(
    financial_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return financial_information_service.get_financial_info_by_id(
        db=db, financial_id=financial_id, user_id=current_user.id
    )


@router.put(
    "/{financial_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update financial information",
    description=(
        "Partially updates an existing financial information record.\n\n"
        "Only the fields included in the request body are updated (PATCH semantics via PUT).\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the startup linked to this record.\n"
        "- Updated numeric fields must be >= 0.\n"
        "- `funding_source` cannot be set to an empty string.\n\n"
        "**Errors:**\n"
        "- `400` — No fields provided / validation error\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own this startup\n"
        "- `404` — Financial information not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "Financial information updated successfully"},
        400: {"description": "Validation error or no fields provided"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Financial information not found"},
        500: {"description": "Internal server error"},
    },
)
def update_financial_info(
    financial_id: int,
    data: FinancialInformationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    financial_information_service.update_financial_info(
        db=db, financial_id=financial_id, user_id=current_user.id, data=data
    )
    return {"message": "Financial information updated successfully"}


@router.delete(
    "/{financial_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete financial information",
    description=(
        "Permanently deletes the financial information record identified by `financial_id`.\n\n"
        "**Rules:**\n"
        "- The authenticated user must own the startup linked to this record.\n\n"
        "**Errors:**\n"
        "- `401` — Unauthorized (missing or invalid JWT)\n"
        "- `403` — User does not own this startup\n"
        "- `404` — Financial information not found\n"
        "- `500` — Internal server error"
    ),
    responses={
        200: {"description": "Financial information deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "User does not own this startup"},
        404: {"description": "Financial information not found"},
        500: {"description": "Internal server error"},
    },
)
def delete_financial_info(
    financial_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    financial_information_service.delete_financial_info(
        db=db, financial_id=financial_id, user_id=current_user.id
    )
    return {"message": "Financial information deleted successfully"}

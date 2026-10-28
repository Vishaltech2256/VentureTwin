"""Authenticated API endpoints for startup business reports."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.report import (
    ReportDetailResponse,
    ReportGenerationResponse,
    ReportListItem,
)
from app.services import report_service

router = APIRouter(tags=["Reports"])


@router.post(
    "/generate/{startup_id}",
    response_model=ReportGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a business report for a startup",
    description=(
        "Creates report metadata for an owned startup after confirming that a "
        "prediction exists. The complete report is assembled on retrieval from the "
        "startup profile, financial, team, location, land, latest prediction, and "
        "all AI suggestions. No PDF file is generated at this stage."
    ),
    responses={
        201: {
            "description": "Report metadata created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Report generated successfully",
                        "report_id": 1,
                        "report_name": "Startup_Report_5_2026.pdf",
                    }
                }
            },
        },
        400: {"description": "A prediction must be generated first"},
        401: {"description": "Missing or invalid JWT token"},
        403: {"description": "Startup belongs to another user"},
        404: {"description": "Startup profile not found"},
        500: {"description": "Internal server error"},
    },
)
def generate_report(
    startup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = report_service.generate_report(
        db=db,
        startup_id=startup_id,
        user_id=current_user.id,
    )
    return {
        "message": "Report generated successfully",
        "report_id": report.report_id,
        "report_name": report.report_name,
    }


@router.get(
    "",
    response_model=list[ReportListItem],
    status_code=status.HTTP_200_OK,
    summary="List reports for the logged-in user",
    description=(
        "Returns metadata for every report linked to a startup owned by the "
        "authenticated user, newest first."
    ),
    responses={
        200: {
            "description": "Report metadata list",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "report_id": 1,
                            "startup_id": 5,
                            "report_name": "Startup_Report_5_2026.pdf",
                            "report_path": "/reports/Startup_Report_5.pdf",
                            "generated_on": "2026-07-18T10:30:00",
                        }
                    ]
                }
            },
        },
        401: {"description": "Missing or invalid JWT token"},
        500: {"description": "Internal server error"},
    },
)
def get_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return report_service.get_reports(db=db, user_id=current_user.id)


@router.get(
    "/{report_id}",
    response_model=ReportDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get one complete business report",
    description=(
        "Returns the current complete business report for a stored report record. "
        "The report includes startup, financial, team, location, land, latest "
        "prediction, and all generated AI suggestions."
    ),
    responses={
        401: {"description": "Missing or invalid JWT token"},
        403: {"description": "Report belongs to a startup owned by another user"},
        404: {"description": "Report not found"},
        500: {"description": "Internal server error"},
    },
)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return report_service.get_report(
        db=db,
        report_id=report_id,
        user_id=current_user.id,
    )


@router.delete(
    "/{report_id}",
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Delete one report",
    description=(
        "Permanently deletes report metadata after confirming that its startup is "
        "owned by the authenticated user."
    ),
    responses={
        200: {
            "description": "Report deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Report deleted successfully"}
                }
            },
        },
        401: {"description": "Missing or invalid JWT token"},
        403: {"description": "Report belongs to a startup owned by another user"},
        404: {"description": "Report not found"},
        500: {"description": "Internal server error"},
    },
)
def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report_service.delete_report(
        db=db,
        report_id=report_id,
        user_id=current_user.id,
    )
    return {"message": "Report deleted successfully"}

# app/services/financial_information_service.py

import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.startup_profile import FinancialInformation, StartupProfile
from app.schemas.financial_information import FinancialInformationCreate, FinancialInformationUpdate

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_startup_and_verify_ownership(db: Session, startup_id: int, user_id: int) -> StartupProfile:
    """Fetch the startup profile and assert that it belongs to the requesting user."""
    startup = db.query(StartupProfile).filter(StartupProfile.startup_id == startup_id).first()
    if not startup:
        logger.warning(f"Startup profile not found: startup_id={startup_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found"
        )
    if startup.user_id != user_id:
        logger.warning(
            f"Forbidden: user_id={user_id} attempted to access startup_id={startup_id} "
            f"owned by user_id={startup.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this startup profile"
        )
    return startup


def _get_financial_record(db: Session, financial_id: int) -> FinancialInformation:
    """Fetch a FinancialInformation record by its primary key or raise 404."""
    record = db.query(FinancialInformation).filter(
        FinancialInformation.financial_id == financial_id
    ).first()
    if not record:
        logger.warning(f"Financial information not found: financial_id={financial_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial information not found"
        )
    return record


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------

def create_financial_info(
    db: Session,
    user_id: int,
    data: FinancialInformationCreate
) -> FinancialInformation:
    """
    Create a new financial information record for a startup.

    - Validates that the startup exists and belongs to the authenticated user.
    - Raises 409 Conflict if a financial record already exists for this startup.
    """
    logger.info(f"Creating financial info for startup_id={data.startup_id} by user_id={user_id}")

    # Verify startup ownership
    _get_startup_and_verify_ownership(db, data.startup_id, user_id)

    # Check for duplicate financial record
    existing = db.query(FinancialInformation).filter(
        FinancialInformation.startup_id == data.startup_id
    ).first()
    if existing:
        logger.warning(f"Financial info already exists for startup_id={data.startup_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Financial information already exists for this startup. Use PUT to update it."
        )

    try:
        # Manually compute the next primary key to match the project's convention
        max_id = db.query(func.max(FinancialInformation.financial_id)).scalar() or 0
        next_id = max_id + 1

        record = FinancialInformation(
            financial_id=next_id,
            startup_id=data.startup_id,
            initial_budget=data.initial_budget,
            monthly_expenses=data.monthly_expenses,
            expected_monthly_revenue=data.expected_monthly_revenue,
            funding_source=data.funding_source,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        logger.info(f"Financial info created: financial_id={record.financial_id}")
        return record
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create financial info for startup_id={data.startup_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the financial information."
        )


def get_user_financial_info(db: Session, user_id: int) -> list[FinancialInformation]:
    """
    Return all financial information records that belong to the authenticated user
    (i.e., all records whose parent startup is owned by this user).
    """
    logger.info(f"Fetching all financial info for user_id={user_id}")
    records = (
        db.query(FinancialInformation)
        .join(StartupProfile, FinancialInformation.startup_id == StartupProfile.startup_id)
        .filter(StartupProfile.user_id == user_id)
        .all()
    )
    return records


def get_financial_info(
    db: Session,
    identifier: int,
    user_id: int
) -> FinancialInformation:
    """Fetch by financial_id or startup_id."""
    startup = db.query(StartupProfile).filter(StartupProfile.startup_id == identifier).first()
    if startup:
        if startup.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        record = db.query(FinancialInformation).filter(FinancialInformation.startup_id == identifier).first()
        if record:
            return record

    record = db.query(FinancialInformation).filter(FinancialInformation.financial_id == identifier).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial information not found")
    _get_startup_and_verify_ownership(db, record.startup_id, user_id)
    return record


def get_financial_info_by_id(
    db: Session,
    financial_id: int,
    user_id: int
) -> FinancialInformation:
    return get_financial_info(db, financial_id, user_id)


def upsert_financial_info(
    db: Session,
    identifier: int,
    user_id: int,
    data: FinancialInformationUpdate
) -> FinancialInformation:
    """Upsert financial info by either startup_id or financial_id."""
    startup = db.query(StartupProfile).filter(StartupProfile.startup_id == identifier).first()
    if startup:
        if startup.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        record = db.query(FinancialInformation).filter(FinancialInformation.startup_id == identifier).first()
        if not record:
            max_id = db.query(func.max(FinancialInformation.financial_id)).scalar() or 0
            record = FinancialInformation(
                financial_id=max_id + 1,
                startup_id=identifier,
                initial_budget=data.initial_budget or 0.0,
                monthly_expenses=data.monthly_expenses or 0.0,
                expected_monthly_revenue=data.expected_monthly_revenue or 0.0,
                funding_source=data.funding_source or "Self-Funded"
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
    else:
        record = db.query(FinancialInformation).filter(FinancialInformation.financial_id == identifier).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial information or startup not found")
        _get_startup_and_verify_ownership(db, record.startup_id, user_id)

    update_data = data.model_dump(exclude_unset=True)
    for field in ["initial_budget", "monthly_expenses", "expected_monthly_revenue", "funding_source"]:
        if field in update_data and update_data[field] is not None:
            setattr(record, field, update_data[field])

    db.commit()
    db.refresh(record)
    return record


def update_financial_info(
    db: Session,
    financial_id: int,
    user_id: int,
    data: FinancialInformationUpdate
) -> FinancialInformation:
    return upsert_financial_info(db, financial_id, user_id, data)


def delete_financial_info(db: Session, financial_id: int, user_id: int) -> None:
    """
    Permanently delete a financial information record.

    - Raises 404 if the record does not exist.
    - Raises 403 if the record belongs to a startup owned by a different user.
    """
    logger.info(f"Deleting financial_id={financial_id} by user_id={user_id}")
    record = db.query(FinancialInformation).filter(
        (FinancialInformation.financial_id == financial_id) | (FinancialInformation.startup_id == financial_id)
    ).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial information not found"
        )
    _get_startup_and_verify_ownership(db, record.startup_id, user_id)

    try:
        db.delete(record)
        db.commit()
        logger.info(f"Financial info deleted: financial_id={record.financial_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete financial_id={record.financial_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the financial information."
        )

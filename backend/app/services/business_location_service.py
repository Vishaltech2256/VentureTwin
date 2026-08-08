# app/services/business_location_service.py

import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.startup_profile import BusinessLocation, StartupProfile
from app.schemas.business_location import BusinessLocationCreate, BusinessLocationUpdate

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


def _get_location_record(db: Session, location_id: int) -> BusinessLocation:
    """Fetch a BusinessLocation record by its primary key or raise 404."""
    record = db.query(BusinessLocation).filter(
        BusinessLocation.location_id == location_id
    ).first()
    if not record:
        logger.warning(f"Business location not found: location_id={location_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business location not found"
        )
    return record


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------

def create_business_location(
    db: Session,
    user_id: int,
    data: BusinessLocationCreate
) -> BusinessLocation:
    """
    Create a new business location record for a startup.

    - Validates that the startup exists and belongs to the authenticated user.
    - Raises 409 Conflict if a business location already exists for this startup.
    """
    logger.info(f"Creating business location for startup_id={data.startup_id} by user_id={user_id}")

    # Verify startup existence and ownership
    _get_startup_and_verify_ownership(db, data.startup_id, user_id)

    # Prevent duplicate location records per startup
    existing = db.query(BusinessLocation).filter(
        BusinessLocation.startup_id == data.startup_id
    ).first()
    if existing:
        logger.warning(f"Business location already exists for startup_id={data.startup_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Business location already exists for this startup. Use PUT to update it."
        )

    try:
        # Manually compute next primary key — consistent with project convention
        max_id = db.query(func.max(BusinessLocation.location_id)).scalar() or 0
        next_id = max_id + 1

        record = BusinessLocation(
            location_id=next_id,
            startup_id=data.startup_id,
            country=data.country,
            state=data.state,
            city=data.city,
            business_address=data.business_address,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        logger.info(f"Business location created: location_id={record.location_id}")
        return record
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create business location for startup_id={data.startup_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the business location."
        )


def get_business_location(db: Session, user_id: int) -> list[BusinessLocation]:
    """
    Return all business location records that belong to the authenticated user
    (i.e., all records whose parent startup is owned by this user).
    """
    logger.info(f"Fetching all business locations for user_id={user_id}")
    records = (
        db.query(BusinessLocation)
        .join(StartupProfile, BusinessLocation.startup_id == StartupProfile.startup_id)
        .filter(StartupProfile.user_id == user_id)
        .all()
    )
    return records


def get_business_location_by_id(
    db: Session,
    location_id: int,
    user_id: int
) -> BusinessLocation:
    """
    Return a single business location record by its primary key.

    - Raises 404 if the record does not exist.
    - Raises 403 if the record belongs to a startup owned by a different user.
    """
    logger.info(f"Fetching location_id={location_id} for user_id={user_id}")
    record = _get_location_record(db, location_id)

    # Verify ownership via the parent startup
    _get_startup_and_verify_ownership(db, record.startup_id, user_id)
    return record


def update_business_location(
    db: Session,
    location_id: int,
    user_id: int,
    data: BusinessLocationUpdate
) -> BusinessLocation:
    """
    Partially update an existing business location record.

    - Only fields explicitly supplied in the request body are updated.
    - Raises 404 if the record does not exist.
    - Raises 403 if the record belongs to a startup owned by a different user.
    """
    logger.info(f"Updating location_id={location_id} by user_id={user_id}")
    record = _get_location_record(db, location_id)

    # Verify ownership via the parent startup
    _get_startup_and_verify_ownership(db, record.startup_id, user_id)

    try:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update."
            )

        for field, value in update_data.items():
            setattr(record, field, value)

        db.commit()
        db.refresh(record)
        logger.info(f"Business location updated: location_id={location_id}")
        return record
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update location_id={location_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the business location."
        )


def delete_business_location(db: Session, location_id: int, user_id: int) -> None:
    """
    Permanently delete a business location record.

    - Raises 404 if the record does not exist.
    - Raises 403 if the record belongs to a startup owned by a different user.
    """
    logger.info(f"Deleting location_id={location_id} by user_id={user_id}")
    record = _get_location_record(db, location_id)

    # Verify ownership via the parent startup
    _get_startup_and_verify_ownership(db, record.startup_id, user_id)

    try:
        db.delete(record)
        db.commit()
        logger.info(f"Business location deleted: location_id={location_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete location_id={location_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the business location."
        )

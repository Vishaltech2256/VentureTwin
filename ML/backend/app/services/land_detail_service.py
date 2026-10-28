# app/services/land_detail_service.py

import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.startup_profile import LandDetail, StartupProfile
from app.schemas.land_detail import LandDetailsCreate, LandDetailsUpdate

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


def _get_land_record(db: Session, land_id: int) -> LandDetail:
    """Fetch a LandDetail record by its primary key or raise 404."""
    record = db.query(LandDetail).filter(LandDetail.land_id == land_id).first()
    if not record:
        logger.warning(f"Land details not found: land_id={land_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land details not found"
        )
    return record


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------

def create_land_details(
    db: Session,
    user_id: int,
    data: LandDetailsCreate
) -> LandDetail:
    """
    Create a new land details record for a startup.

    - Validates that the startup exists and belongs to the authenticated user.
    - Raises 409 Conflict if a land details record already exists for this startup.
    """
    logger.info(f"Creating land details for startup_id={data.startup_id} by user_id={user_id}")

    # Verify startup existence and ownership
    _get_startup_and_verify_ownership(db, data.startup_id, user_id)

    # Prevent duplicate land detail records per startup
    existing = db.query(LandDetail).filter(
        LandDetail.startup_id == data.startup_id
    ).first()
    if existing:
        logger.warning(f"Land details already exists for startup_id={data.startup_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Land details already exist for this startup. Use PUT to update them."
        )

    try:
        # Manually compute next primary key — consistent with project convention
        max_id = db.query(func.max(LandDetail.land_id)).scalar() or 0
        next_id = max_id + 1

        record = LandDetail(
            land_id=next_id,
            startup_id=data.startup_id,
            has_land=data.has_land,
            land_status=data.land_status,
            land_area_sqft=data.land_area_sqft,
            land_location=data.land_location,
            land_value=data.land_value,
            monthly_rent=data.monthly_rent,
            expandable=data.expandable,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        logger.info(f"Land details created: land_id={record.land_id}")
        return record
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create land details for startup_id={data.startup_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the land details."
        )


def get_land_details(db: Session, user_id: int) -> list[LandDetail]:
    """
    Return all land detail records that belong to the authenticated user
    (i.e., all records whose parent startup is owned by this user).
    """
    logger.info(f"Fetching all land details for user_id={user_id}")
    records = (
        db.query(LandDetail)
        .join(StartupProfile, LandDetail.startup_id == StartupProfile.startup_id)
        .filter(StartupProfile.user_id == user_id)
        .all()
    )
    return records


def get_land_details_by_id(
    db: Session,
    land_id: int,
    user_id: int
) -> LandDetail:
    """
    Return a single land details record by its primary key.

    - Raises 404 if the record does not exist.
    - Raises 403 if the record belongs to a startup owned by a different user.
    """
    logger.info(f"Fetching land_id={land_id} for user_id={user_id}")
    record = _get_land_record(db, land_id)

    # Verify ownership via the parent startup
    _get_startup_and_verify_ownership(db, record.startup_id, user_id)
    return record


def update_land_details(
    db: Session,
    land_id: int,
    user_id: int,
    data: LandDetailsUpdate
) -> LandDetail:
    """
    Partially update an existing land details record.

    - Only fields explicitly supplied in the request body are updated.
    - Raises 404 if the record does not exist.
    - Raises 403 if the record belongs to a startup owned by a different user.
    """
    logger.info(f"Updating land_id={land_id} by user_id={user_id}")
    record = _get_land_record(db, land_id)

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
        logger.info(f"Land details updated: land_id={land_id}")
        return record
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update land_id={land_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the land details."
        )


def delete_land_details(db: Session, land_id: int, user_id: int) -> None:
    """
    Permanently delete a land details record.

    - Raises 404 if the record does not exist.
    - Raises 403 if the record belongs to a startup owned by a different user.
    """
    logger.info(f"Deleting land_id={land_id} by user_id={user_id}")
    record = _get_land_record(db, land_id)

    # Verify ownership via the parent startup
    _get_startup_and_verify_ownership(db, record.startup_id, user_id)

    try:
        db.delete(record)
        db.commit()
        logger.info(f"Land details deleted: land_id={land_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete land_id={land_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the land details."
        )

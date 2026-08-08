# app/services/team_information_service.py

import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.startup_profile import TeamInformation, StartupProfile
from app.schemas.team_information import TeamInformationCreate, TeamInformationUpdate

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_startup_and_verify_ownership(db: Session, startup_id: int, user_id: int) -> StartupProfile:
    """Fetch the startup profile and assert it belongs to the requesting user."""
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


def _get_team_record(db: Session, team_id: int) -> TeamInformation:
    """Fetch a TeamInformation record by its primary key or raise 404."""
    record = db.query(TeamInformation).filter(TeamInformation.team_id == team_id).first()
    if not record:
        logger.warning(f"Team information not found: team_id={team_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team information not found"
        )
    return record


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------

def create_team_information(
    db: Session,
    user_id: int,
    data: TeamInformationCreate
) -> TeamInformation:
    """
    Create a new team information record for a startup.

    - Validates that the startup exists and belongs to the authenticated user.
    - Raises 409 Conflict if a team record already exists for this startup.
    """
    logger.info(f"Creating team info for startup_id={data.startup_id} by user_id={user_id}")

    # Verify startup existence and ownership
    _get_startup_and_verify_ownership(db, data.startup_id, user_id)

    # Prevent duplicate team records per startup
    existing = db.query(TeamInformation).filter(
        TeamInformation.startup_id == data.startup_id
    ).first()
    if existing:
        logger.warning(f"Team info already exists for startup_id={data.startup_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team information already exists for this startup. Use PUT to update it."
        )

    try:
        # Manually compute next primary key — consistent with project convention
        max_id = db.query(func.max(TeamInformation.team_id)).scalar() or 0
        next_id = max_id + 1

        record = TeamInformation(
            team_id=next_id,
            startup_id=data.startup_id,
            founder_name=data.founder_name,
            co_founder_name=data.co_founder_name,
            number_of_employees=data.number_of_employees,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        logger.info(f"Team info created: team_id={record.team_id}")
        return record
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create team info for startup_id={data.startup_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the team information."
        )


def get_team_information(db: Session, startup_id: int, user_id: int) -> TeamInformation:
    """
    Return the team information record for a given startup.

    - Raises 403 if the startup does not belong to the authenticated user.
    - Raises 404 if the startup or its team record does not exist.
    """
    logger.info(f"Fetching team info for startup_id={startup_id} by user_id={user_id}")

    # Verify startup existence and ownership first
    _get_startup_and_verify_ownership(db, startup_id, user_id)

    record = db.query(TeamInformation).filter(
        TeamInformation.startup_id == startup_id
    ).first()
    if not record:
        logger.warning(f"No team info found for startup_id={startup_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team information not found for this startup"
        )
    return record


def update_team_information(
    db: Session,
    team_id: int,
    user_id: int,
    data: TeamInformationUpdate
) -> TeamInformation:
    """
    Partially update an existing team information record.

    - Only fields explicitly supplied in the request body are updated.
    - Raises 404 if the record does not exist.
    - Raises 403 if the record belongs to a startup owned by a different user.
    """
    logger.info(f"Updating team_id={team_id} by user_id={user_id}")
    record = _get_team_record(db, team_id)

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
        logger.info(f"Team info updated: team_id={team_id}")
        return record
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update team_id={team_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the team information."
        )


def delete_team_information(db: Session, team_id: int, user_id: int) -> None:
    """
    Permanently delete a team information record.

    - Raises 404 if the record does not exist.
    - Raises 403 if the record belongs to a startup owned by a different user.
    """
    logger.info(f"Deleting team_id={team_id} by user_id={user_id}")
    record = _get_team_record(db, team_id)

    # Verify ownership via the parent startup
    _get_startup_and_verify_ownership(db, record.startup_id, user_id)

    try:
        db.delete(record)
        db.commit()
        logger.info(f"Team info deleted: team_id={team_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete team_id={team_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the team information."
        )

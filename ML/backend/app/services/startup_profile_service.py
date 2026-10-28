from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
import logging
from app.models.startup_profile import (
    StartupProfile,
    TeamInformation,
    FinancialInformation,
    BusinessLocation,
    LandDetail
)
from app.schemas.startup_profile import CreateStartupProfile, UpdateStartupProfile

logger = logging.getLogger(__name__)

def create_startup_profile(db: Session, user_id: int, data: CreateStartupProfile) -> StartupProfile:
    logger.info(f"Creating startup profile for user_id={user_id} with name={data.startup_name}")
    try:
        # Calculate manually next ID for startup profile
        max_startup_id = db.query(func.max(StartupProfile.startup_id)).scalar() or 0
        next_startup_id = max_startup_id + 1

        db_profile = StartupProfile(
            startup_id=next_startup_id,
            user_id=user_id,
            startup_name=data.startup_name,
            startup_description=data.startup_description,
            business_type=data.business_type,
            industry=data.industry,
            startup_stage=data.startup_stage,
            target_market=data.target_market
        )
        db.add(db_profile)
        db.flush()  # Push to database to ensure constraint safety before child creation

        # Calculate manually next ID for team info
        max_team_id = db.query(func.max(TeamInformation.team_id)).scalar() or 0
        next_team_id = max_team_id + 1
        db_team = TeamInformation(
            team_id=next_team_id,
            startup_id=next_startup_id,
            founder_name=data.founder_name,
            has_cofounder=data.has_cofounder,
            number_of_employees=data.number_of_employees
        )
        db.add(db_team)

        # Calculate manually next ID for financial info
        max_financial_id = db.query(func.max(FinancialInformation.financial_id)).scalar() or 0
        next_financial_id = max_financial_id + 1
        db_financial = FinancialInformation(
            financial_id=next_financial_id,
            startup_id=next_startup_id,
            initial_budget=data.initial_budget,
            monthly_expenses=data.monthly_expenses,
            expected_monthly_revenue=data.expected_monthly_revenue,
            funding_source=data.funding_source
        )
        db.add(db_financial)

        # Calculate manually next ID for business location
        max_location_id = db.query(func.max(BusinessLocation.location_id)).scalar() or 0
        next_location_id = max_location_id + 1
        db_location = BusinessLocation(
            location_id=next_location_id,
            startup_id=next_startup_id,
            country=data.country,
            state=data.state,
            city=data.city,
            business_address=data.business_address
        )
        db.add(db_location)

        # Calculate manually next ID for land detail
        max_land_id = db.query(func.max(LandDetail.land_id)).scalar() or 0
        next_land_id = max_land_id + 1
        db_land = LandDetail(
            land_id=next_land_id,
            startup_id=next_startup_id,
            has_land=data.has_land,
            land_status=data.land_status,
            land_area_sqft=data.land_area_sqft,
            land_location=data.land_location,
            land_value=data.land_value,
            expandable=data.expandable,
            monthly_rent=data.monthly_rent
        )
        db.add(db_land)

        db.commit()
        db.refresh(db_profile)
        logger.info(f"Startup profile created successfully with ID={db_profile.startup_id}")
        return db_profile
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create startup profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the startup profile."
        )

def get_startup_profile(db: Session, startup_id: int) -> StartupProfile:
    db_profile = db.query(StartupProfile).filter(StartupProfile.startup_id == startup_id).first()
    if not db_profile:
        logger.warning(f"Startup profile not found: ID={startup_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found"
        )
    return db_profile

def check_ownership(startup: StartupProfile, user_id: int) -> None:
    if startup.user_id != user_id:
        logger.warning(f"Forbidden access: user={user_id} tried to access startup={startup.startup_id} owned by user={startup.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this startup profile"
        )

def list_user_startup_profiles(db: Session, user_id: int) -> list[StartupProfile]:
    return db.query(StartupProfile).filter(StartupProfile.user_id == user_id).all()

def update_startup_profile(db: Session, startup_id: int, user_id: int, data: UpdateStartupProfile) -> StartupProfile:
    db_profile = get_startup_profile(db, startup_id)
    check_ownership(db_profile, user_id)
    
    logger.info(f"Updating startup profile ID={startup_id}")
    try:
        # Update core StartupProfile attributes
        update_data = data.model_dump(exclude_unset=True)
        for key in ["startup_name", "startup_description", "business_type", "industry", "startup_stage", "target_market"]:
            if key in update_data:
                setattr(db_profile, key, update_data[key])
        
        # Update Team information
        if db_profile.team_info is not None:
            for key in ["founder_name", "has_cofounder", "number_of_employees"]:
                if key in update_data:
                    setattr(db_profile.team_info, key, update_data[key])
        
        # Update Financial information
        if db_profile.financial_info is not None:
            for key in ["initial_budget", "monthly_expenses", "expected_monthly_revenue", "funding_source"]:
                if key in update_data:
                    setattr(db_profile.financial_info, key, update_data[key])
                    
        # Update Business Location
        if db_profile.location is not None:
            for key in ["country", "state", "city", "business_address"]:
                if key in update_data:
                    setattr(db_profile.location, key, update_data[key])

        # Update Land Detail
        if db_profile.land_detail is not None:
            for key in ["has_land", "land_status", "land_area_sqft", "land_location", "land_value", "expandable", "monthly_rent"]:
                if key in update_data:
                    setattr(db_profile.land_detail, key, update_data[key])
            
            # Apply dynamic business rules during partial update if land_status or monthly_rent was touched
            status_val = db_profile.land_detail.land_status
            if status_val:
                status_lower = status_val.lower()
                if "rent" in status_lower:
                    if db_profile.land_detail.monthly_rent is None:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="monthly_rent is required when land status is renting"
                        )
                elif "own" in status_lower:
                    db_profile.land_detail.monthly_rent = None

        db.commit()
        db.refresh(db_profile)
        logger.info(f"Startup profile ID={startup_id} updated successfully")
        return db_profile
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update startup profile ID={startup_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the startup profile."
        )

def delete_startup_profile(db: Session, startup_id: int, user_id: int) -> None:
    db_profile = get_startup_profile(db, startup_id)
    check_ownership(db_profile, user_id)
    
    logger.info(f"Deleting startup profile ID={startup_id}")
    try:
        db.delete(db_profile)
        db.commit()
        logger.info(f"Startup profile ID={startup_id} deleted successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete startup profile ID={startup_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the startup profile."
        )

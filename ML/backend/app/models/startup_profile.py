from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

class StartupProfile(Base):
    __tablename__ = "startup_profiles"

    startup_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    startup_name: Mapped[str] = mapped_column(String(150), nullable=False)
    startup_description: Mapped[str] = mapped_column(Text, nullable=False)
    business_type: Mapped[str] = mapped_column(String(100), nullable=False)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    startup_stage: Mapped[str] = mapped_column(String(100), nullable=False)
    target_market: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", backref="startup_profiles")
    
    team_info: Mapped["TeamInformation"] = relationship(
        "TeamInformation", back_populates="startup_profile", uselist=False, cascade="all, delete-orphan", lazy="joined"
    )
    financial_info: Mapped["FinancialInformation"] = relationship(
        "FinancialInformation", back_populates="startup_profile", uselist=False, cascade="all, delete-orphan", lazy="joined"
    )
    location: Mapped["BusinessLocation"] = relationship(
        "BusinessLocation", back_populates="startup_profile", uselist=False, cascade="all, delete-orphan", lazy="joined"
    )
    land_detail: Mapped["LandDetail"] = relationship(
        "LandDetail", back_populates="startup_profile", uselist=False, cascade="all, delete-orphan", lazy="joined"
    )

    # Property Getters for Unified Pydantic Schema Serialization
    @property
    def initial_budget(self) -> Optional[float]:
        return self.financial_info.initial_budget if self.financial_info is not None else None

    @property
    def monthly_expenses(self) -> Optional[float]:
        return self.financial_info.monthly_expenses if self.financial_info is not None else None

    @property
    def expected_monthly_revenue(self) -> Optional[float]:
        return self.financial_info.expected_monthly_revenue if self.financial_info is not None else None

    @property
    def funding_source(self) -> Optional[str]:
        return self.financial_info.funding_source if self.financial_info is not None else None

    @property
    def founder_name(self) -> Optional[str]:
        return self.team_info.founder_name if self.team_info is not None else None

    @property
    def has_cofounder(self) -> Optional[bool]:
        return self.team_info.has_cofounder if self.team_info is not None else None

    @property
    def number_of_employees(self) -> Optional[int]:
        return self.team_info.number_of_employees if self.team_info is not None else None

    @property
    def country(self) -> Optional[str]:
        return self.location.country if self.location is not None else None

    @property
    def state(self) -> Optional[str]:
        return self.location.state if self.location is not None else None

    @property
    def city(self) -> Optional[str]:
        return self.location.city if self.location is not None else None

    @property
    def business_address(self) -> Optional[str]:
        return self.location.business_address if self.location is not None else None

    @property
    def has_land(self) -> Optional[bool]:
        return self.land_detail.has_land if self.land_detail is not None else None

    @property
    def land_status(self) -> Optional[str]:
        return self.land_detail.land_status if self.land_detail is not None else None

    @property
    def land_area_sqft(self) -> Optional[float]:
        return self.land_detail.land_area_sqft if self.land_detail is not None else None

    @property
    def land_location(self) -> Optional[str]:
        return self.land_detail.land_location if self.land_detail is not None else None

    @property
    def land_value(self) -> Optional[float]:
        return self.land_detail.land_value if self.land_detail is not None else None

    @property
    def monthly_rent(self) -> Optional[float]:
        return self.land_detail.monthly_rent if self.land_detail is not None else None

    @property
    def expandable(self) -> Optional[bool]:
        return self.land_detail.expandable if self.land_detail is not None else None


class TeamInformation(Base):
    __tablename__ = "team_information"

    team_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    startup_id: Mapped[int] = mapped_column(Integer, ForeignKey("startup_profiles.startup_id", ondelete="CASCADE"), nullable=False, index=True)
    founder_name: Mapped[str] = mapped_column(String(100), nullable=False)
    has_cofounder: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    number_of_employees: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    startup_profile: Mapped["StartupProfile"] = relationship("StartupProfile", back_populates="team_info")


class FinancialInformation(Base):
    __tablename__ = "financial_information"

    financial_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    startup_id: Mapped[int] = mapped_column(Integer, ForeignKey("startup_profiles.startup_id", ondelete="CASCADE"), nullable=False, index=True)
    initial_budget: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    monthly_expenses: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    expected_monthly_revenue: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    funding_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    startup_profile: Mapped["StartupProfile"] = relationship("StartupProfile", back_populates="financial_info")


class BusinessLocation(Base):
    __tablename__ = "business_locations"

    location_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    startup_id: Mapped[int] = mapped_column(Integer, ForeignKey("startup_profiles.startup_id", ondelete="CASCADE"), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    business_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    startup_profile: Mapped["StartupProfile"] = relationship("StartupProfile", back_populates="location")


class LandDetail(Base):
    __tablename__ = "land_details"

    land_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    startup_id: Mapped[int] = mapped_column(Integer, ForeignKey("startup_profiles.startup_id", ondelete="CASCADE"), nullable=False, index=True)
    has_land: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    land_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    land_area_sqft: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    land_location: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    land_value: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    expandable: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    monthly_rent: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    startup_profile: Mapped["StartupProfile"] = relationship("StartupProfile", back_populates="land_detail")


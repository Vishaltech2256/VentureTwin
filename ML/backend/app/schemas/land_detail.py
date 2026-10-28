# app/schemas/land_detail.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class LandDetailsCreate(BaseModel):
    """Schema for creating a new land details record."""

    startup_id: int = Field(
        ...,
        description="ID of the startup this land details record belongs to",
        examples=[1]
    )
    has_land: Optional[bool] = Field(
        default=None,
        description="Whether the startup owns or occupies a physical land/plot",
        examples=[True]
    )
    land_status: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Ownership or usage status of the land (required, max 100 chars)",
        examples=["Owned"]
    )
    land_area_sqft: Optional[int] = Field(
        default=None,
        ge=0,
        description="Area of the land in square feet (must be >= 0 if provided)",
        examples=[5000]
    )
    land_location: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Physical address or geographic description of the land (max 255 chars)",
        examples=["Plot 12, MIDC Industrial Area, Pune - 411019"]
    )
    land_value: Optional[float] = Field(
        default=None,
        ge=0,
        description="Current market value of the land in currency units (must be >= 0)",
        examples=[2500000.00]
    )
    monthly_rent: Optional[float] = Field(
        default=None,
        ge=0,
        description="Monthly rent paid if the land is leased (must be >= 0)",
        examples=[45000.00]
    )
    expandable: Optional[bool] = Field(
        default=None,
        description="Whether the land can be expanded in the future",
        examples=[True]
    )

    @field_validator("land_status")
    @classmethod
    def land_status_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("land_status cannot be empty or whitespace")
        return v.strip()

    @field_validator("land_location")
    @classmethod
    def land_location_strip(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("land_location cannot be an empty or whitespace string")
            return stripped
        return v


class LandDetailsUpdate(BaseModel):
    """Schema for partially updating an existing land details record.
    All fields are optional — only supplied fields will be written to the database.
    """

    has_land: Optional[bool] = Field(
        default=None,
        description="Updated land ownership flag",
        examples=[False]
    )
    land_status: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated land status (cannot be empty if provided, max 100 chars)",
        examples=["Leased"]
    )
    land_area_sqft: Optional[int] = Field(
        default=None,
        ge=0,
        description="Updated land area in square feet (must be >= 0 if provided)",
        examples=[7500]
    )
    land_location: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Updated land location (max 255 chars)",
        examples=["Survey No. 34, Hinjewadi Phase 3, Pune - 411057"]
    )
    land_value: Optional[float] = Field(
        default=None,
        ge=0,
        description="Updated land value (must be >= 0 if provided)",
        examples=[3000000.00]
    )
    monthly_rent: Optional[float] = Field(
        default=None,
        ge=0,
        description="Updated monthly rent (must be >= 0 if provided)",
        examples=[55000.00]
    )
    expandable: Optional[bool] = Field(
        default=None,
        description="Updated expandability flag",
        examples=[False]
    )

    @field_validator("land_status")
    @classmethod
    def land_status_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("land_status cannot be empty or whitespace")
            return v.strip()
        return v

    @field_validator("land_location")
    @classmethod
    def land_location_strip(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("land_location cannot be an empty or whitespace string")
            return stripped
        return v


class LandDetailsResponse(BaseModel):
    """Schema returned in API responses for land details."""

    land_id: int = Field(..., description="Unique identifier of the land details record")
    startup_id: int = Field(..., description="ID of the related startup profile")
    has_land: Optional[bool] = Field(default=None, description="Whether the startup owns or occupies land")
    land_status: str = Field(..., description="Ownership or usage status of the land")
    land_area_sqft: Optional[int] = Field(default=None, description="Area of the land in square feet")
    land_location: Optional[str] = Field(default=None, description="Physical address of the land")
    land_value: Optional[float] = Field(default=None, description="Current market value of the land")
    monthly_rent: Optional[float] = Field(default=None, description="Monthly rent if leased")
    expandable: Optional[bool] = Field(default=None, description="Whether the land can be expanded")
    created_at: datetime = Field(..., description="Timestamp when the record was created")

    model_config = {"from_attributes": True}

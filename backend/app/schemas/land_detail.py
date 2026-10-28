# app/schemas/land_detail.py

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, AliasChoices, computed_field


class LandDetailsCreate(BaseModel):
    """Schema for creating a new land details record."""

    startup_id: Optional[int] = Field(
        default=None,
        description="ID of the startup this land details record belongs to (optional if in URL)",
        examples=[1]
    )
    has_land: Optional[bool] = Field(
        default=False,
        description="Whether the startup owns or occupies a physical land/plot",
        examples=[True]
    )
    land_status: Optional[str] = Field(
        default="no_land",
        max_length=100,
        description="Ownership or usage status of the land",
        examples=["Owned"]
    )
    land_area_sqft: Optional[float] = Field(
        default=None,
        ge=0,
        description="Area of the land in square feet",
        examples=[5000]
    )
    land_location: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Physical address or geographic description of the land",
        examples=["Plot 12, MIDC Industrial Area, Pune - 411019"]
    )
    land_value: Optional[float] = Field(
        default=None,
        ge=0,
        description="Current market value of the land in currency units",
        examples=[2500000.00]
    )
    monthly_rent: Optional[float] = Field(
        default=None,
        ge=0,
        description="Monthly rent paid if the land is leased",
        examples=[45000.00]
    )
    expandable: Optional[bool] = Field(
        default=False,
        validation_alias=AliasChoices("expandable", "expansion_available"),
        description="Whether the land can be expanded in the future",
        examples=[True]
    )

    model_config = {"populate_by_name": True}


class LandDetailsUpdate(BaseModel):
    """Schema for partially updating an existing land details record."""

    has_land: Optional[bool] = Field(
        default=None,
        description="Updated land ownership flag",
        examples=[False]
    )
    land_status: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Updated land status",
        examples=["Leased"]
    )
    land_area_sqft: Optional[float] = Field(
        default=None,
        ge=0,
        description="Updated land area in square feet",
        examples=[7500]
    )
    land_location: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Updated land location",
        examples=["Survey No. 34, Hinjewadi Phase 3, Pune - 411057"]
    )
    land_value: Optional[float] = Field(
        default=None,
        ge=0,
        description="Updated land value",
        examples=[3000000.00]
    )
    monthly_rent: Optional[float] = Field(
        default=None,
        ge=0,
        description="Updated monthly rent",
        examples=[55000.00]
    )
    expandable: Optional[bool] = Field(
        default=None,
        validation_alias=AliasChoices("expandable", "expansion_available"),
        description="Updated expandability flag",
        examples=[False]
    )

    model_config = {"populate_by_name": True}


class LandDetailsResponse(BaseModel):
    """Schema returned in API responses for land details."""

    land_id: int = Field(..., description="Unique identifier of the land details record")
    startup_id: int = Field(..., description="ID of the related startup profile")
    has_land: Optional[bool] = Field(default=False, description="Whether the startup owns or occupies land")
    land_status: Optional[str] = Field(default="no_land", description="Ownership or usage status of the land")
    land_area_sqft: Optional[float] = Field(default=None, description="Area of the land in square feet")
    land_location: Optional[str] = Field(default=None, description="Physical address of the land")
    land_value: Optional[float] = Field(default=None, description="Current market value of the land")
    monthly_rent: Optional[float] = Field(default=None, description="Monthly rent if leased")
    expandable: Optional[bool] = Field(default=False, description="Whether the land can be expanded")
    created_at: datetime = Field(..., description="Timestamp when the record was created")
    updated_at: Optional[datetime] = Field(default=None, description="Timestamp when the record was updated")

    @computed_field
    @property
    def expansion_available(self) -> bool:
        return bool(self.expandable)

    model_config = {"from_attributes": True, "populate_by_name": True}


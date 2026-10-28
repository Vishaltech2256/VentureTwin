# app/schemas/business_location.py

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, AliasChoices, computed_field


class BusinessLocationCreate(BaseModel):
    """Schema for creating a new business location record."""

    startup_id: Optional[int] = Field(
        default=None,
        description="ID of the startup this location belongs to (optional if in URL)",
        examples=[1]
    )
    country: Optional[str] = Field(
        default="India",
        max_length=100,
        description="Country where the business is located",
        examples=["India"]
    )
    state: Optional[str] = Field(
        default="Karnataka",
        max_length=100,
        description="State or province where the business is located",
        examples=["Karnataka"]
    )
    city: Optional[str] = Field(
        default="Bengaluru",
        max_length=100,
        description="City where the business is located",
        examples=["Bengaluru"]
    )
    business_address: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("business_address", "address"),
        description="Full street or postal address of the business",
        examples=["101, MG Road, Bengaluru"]
    )
    pincode: Optional[str] = Field(default=None, max_length=20)

    model_config = {"populate_by_name": True}


class BusinessLocationUpdate(BaseModel):
    """Schema for partially updating an existing business location record."""

    country: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Updated country",
        examples=["United States"]
    )
    state: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Updated state or province",
        examples=["California"]
    )
    city: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Updated city",
        examples=["San Francisco"]
    )
    business_address: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("business_address", "address"),
        description="Updated business address",
        examples=["500 Market Street, San Francisco, CA 94105"]
    )
    pincode: Optional[str] = Field(default=None, max_length=20)

    model_config = {"populate_by_name": True}


class BusinessLocationResponse(BaseModel):
    """Schema returned in API responses for business location."""

    location_id: int = Field(..., description="Unique identifier of the location record")
    startup_id: int = Field(..., description="ID of the related startup profile")
    country: Optional[str] = Field(default=None, description="Country where the business is located")
    state: Optional[str] = Field(default=None, description="State or province where the business is located")
    city: Optional[str] = Field(default=None, description="City where the business is located")
    business_address: Optional[str] = Field(default=None, description="Full street or postal address of the business")
    pincode: Optional[str] = Field(default=None)
    created_at: datetime = Field(..., description="Timestamp when the record was created")
    updated_at: Optional[datetime] = Field(default=None, description="Timestamp when the record was updated")

    @computed_field
    @property
    def address(self) -> Optional[str]:
        return self.business_address

    model_config = {"from_attributes": True, "populate_by_name": True}


# app/schemas/business_location.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class BusinessLocationCreate(BaseModel):
    """Schema for creating a new business location record."""

    startup_id: int = Field(
        ...,
        description="ID of the startup this location belongs to",
        examples=[1]
    )
    country: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Country where the business is located (required, max 100 chars)",
        examples=["India"]
    )
    state: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="State or province where the business is located (required, max 100 chars)",
        examples=["Maharashtra"]
    )
    city: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="City where the business is located (required, max 100 chars)",
        examples=["Mumbai"]
    )
    business_address: str = Field(
        ...,
        min_length=1,
        description="Full street or postal address of the business (required)",
        examples=["101, Nariman Point, Mumbai - 400021"]
    )

    @field_validator("country")
    @classmethod
    def country_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("country cannot be empty or whitespace")
        return v.strip()

    @field_validator("state")
    @classmethod
    def state_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("state cannot be empty or whitespace")
        return v.strip()

    @field_validator("city")
    @classmethod
    def city_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("city cannot be empty or whitespace")
        return v.strip()

    @field_validator("business_address")
    @classmethod
    def business_address_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("business_address cannot be empty or whitespace")
        return v.strip()


class BusinessLocationUpdate(BaseModel):
    """Schema for partially updating an existing business location record.
    All fields are optional — only supplied fields will be written to the database.
    """

    country: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated country (max 100 chars, cannot be empty if provided)",
        examples=["United States"]
    )
    state: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated state or province (max 100 chars, cannot be empty if provided)",
        examples=["California"]
    )
    city: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated city (max 100 chars, cannot be empty if provided)",
        examples=["San Francisco"]
    )
    business_address: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Updated business address (cannot be empty if provided)",
        examples=["500 Market Street, San Francisco, CA 94105"]
    )

    @field_validator("country")
    @classmethod
    def country_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("country cannot be empty or whitespace")
            return v.strip()
        return v

    @field_validator("state")
    @classmethod
    def state_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("state cannot be empty or whitespace")
            return v.strip()
        return v

    @field_validator("city")
    @classmethod
    def city_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("city cannot be empty or whitespace")
            return v.strip()
        return v

    @field_validator("business_address")
    @classmethod
    def business_address_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("business_address cannot be empty or whitespace")
            return v.strip()
        return v


class BusinessLocationResponse(BaseModel):
    """Schema returned in API responses for business location."""

    location_id: int = Field(..., description="Unique identifier of the location record")
    startup_id: int = Field(..., description="ID of the related startup profile")
    country: str = Field(..., description="Country where the business is located")
    state: str = Field(..., description="State or province where the business is located")
    city: str = Field(..., description="City where the business is located")
    business_address: Optional[str] = Field(default=None, description="Full street or postal address of the business")
    created_at: datetime = Field(..., description="Timestamp when the record was created")

    model_config = {"from_attributes": True}

# app/schemas/team_information.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TeamInformationCreate(BaseModel):
    """Schema for creating a new team information record."""

    startup_id: int = Field(
        ...,
        description="ID of the startup this team info belongs to",
        examples=[1]
    )
    founder_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Full name of the primary founder (minimum 2 characters)",
        examples=["Jane Doe"]
    )
    co_founder_name: Optional[str] = Field(
        default=None,
        max_length=150,
        description="Full name of the co-founder (optional)",
        examples=["John Smith"]
    )
    number_of_employees: int = Field(
        ...,
        ge=1,
        description="Total number of employees including founders (must be >= 1)",
        examples=[5]
    )

    @field_validator("founder_name")
    @classmethod
    def founder_name_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("founder_name cannot be empty or whitespace")
        return v.strip()

    @field_validator("co_founder_name")
    @classmethod
    def co_founder_name_strip(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("co_founder_name cannot be an empty or whitespace string")
            return stripped
        return v


class TeamInformationUpdate(BaseModel):
    """Schema for partially updating an existing team information record.
    All fields are optional — only supplied fields will be written to the database.
    """

    founder_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=150,
        description="Updated founder name (minimum 2 characters)",
        examples=["Jane Doe"]
    )
    co_founder_name: Optional[str] = Field(
        default=None,
        max_length=150,
        description="Updated co-founder name (pass null to clear)",
        examples=["Alice Brown"]
    )
    number_of_employees: Optional[int] = Field(
        default=None,
        ge=1,
        description="Updated employee count (must be >= 1 if provided)",
        examples=[10]
    )

    @field_validator("founder_name")
    @classmethod
    def founder_name_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("founder_name cannot be empty or whitespace")
            return v.strip()
        return v

    @field_validator("co_founder_name")
    @classmethod
    def co_founder_name_strip(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("co_founder_name cannot be an empty or whitespace string")
            return stripped
        return v


class TeamInformationResponse(BaseModel):
    """Schema returned in API responses for team information."""

    team_id: int = Field(..., description="Unique identifier of the team record")
    startup_id: int = Field(..., description="ID of the related startup profile")
    founder_name: str = Field(..., description="Full name of the primary founder")
    co_founder_name: Optional[str] = Field(default=None, description="Full name of the co-founder")
    number_of_employees: int = Field(..., description="Total number of employees")
    created_at: datetime = Field(..., description="Timestamp when the record was created")

    model_config = {"from_attributes": True}

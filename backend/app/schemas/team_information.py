# app/schemas/team_information.py

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator, AliasChoices, computed_field


class TeamInformationCreate(BaseModel):
    """Schema for creating a new team information record."""

    startup_id: Optional[int] = Field(
        default=None,
        description="ID of the startup this team info belongs to (optional if provided in URL)",
        examples=[1]
    )
    founder_name: Optional[str] = Field(
        default="Founder",
        max_length=150,
        description="Full name of the primary founder",
        examples=["Jane Doe"]
    )
    co_founder_name: Optional[str] = Field(
        default=None,
        max_length=150,
        description="Full name of the co-founder (optional)",
        examples=["John Smith"]
    )
    number_of_employees: Optional[int] = Field(
        default=1,
        ge=0,
        validation_alias=AliasChoices("number_of_employees", "employee_count"),
        description="Total number of employees including founders",
        examples=[5]
    )
    has_technical_cofounder: Optional[bool] = Field(
        default=False,
        validation_alias=AliasChoices("has_cofounder", "has_technical_cofounder"),
        description="Indicates if team has technical cofounder"
    )
    founder_experience_years: Optional[int] = Field(default=None, ge=0)
    founder_education: Optional[str] = Field(default=None)
    team_skills: Optional[str] = Field(default=None)

    model_config = {"populate_by_name": True}

    @field_validator("founder_name", mode="before")
    @classmethod
    def founder_name_default(cls, v: Any) -> str:
        if v is None or not str(v).strip():
            return "Founder"
        return str(v).strip()


class TeamInformationUpdate(BaseModel):
    """Schema for partially updating an existing team information record."""

    founder_name: Optional[str] = Field(
        default=None,
        max_length=150,
        description="Updated founder name",
        examples=["Jane Doe"]
    )
    co_founder_name: Optional[str] = Field(
        default=None,
        max_length=150,
        description="Updated co-founder name",
        examples=["Alice Brown"]
    )
    number_of_employees: Optional[int] = Field(
        default=None,
        ge=0,
        validation_alias=AliasChoices("number_of_employees", "employee_count"),
        description="Updated employee count",
        examples=[10]
    )
    has_technical_cofounder: Optional[bool] = Field(
        default=None,
        validation_alias=AliasChoices("has_cofounder", "has_technical_cofounder"),
    )
    founder_experience_years: Optional[int] = Field(default=None, ge=0)
    founder_education: Optional[str] = Field(default=None)
    team_skills: Optional[str] = Field(default=None)

    model_config = {"populate_by_name": True}


class TeamInformationResponse(BaseModel):
    """Schema returned in API responses for team information."""

    team_id: int = Field(..., description="Unique identifier of the team record")
    startup_id: int = Field(..., description="ID of the related startup profile")
    founder_name: Optional[str] = Field(default="Founder", description="Full name of the primary founder")
    co_founder_name: Optional[str] = Field(default=None, description="Full name of the co-founder")
    number_of_employees: Optional[int] = Field(default=1, description="Total number of employees")
    has_cofounder: Optional[bool] = Field(default=False)
    founder_experience_years: Optional[int] = Field(default=None)
    founder_education: Optional[str] = Field(default=None)
    team_skills: Optional[str] = Field(default=None)
    created_at: datetime = Field(..., description="Timestamp when the record was created")
    updated_at: Optional[datetime] = Field(default=None, description="Timestamp when the record was updated")

    @computed_field
    @property
    def employee_count(self) -> Optional[int]:
        return self.number_of_employees

    @computed_field
    @property
    def has_technical_cofounder(self) -> bool:
        return bool(self.has_cofounder or (self.co_founder_name and self.co_founder_name.strip()))

    model_config = {"from_attributes": True, "populate_by_name": True}


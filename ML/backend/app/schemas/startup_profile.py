from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator

class StartupProfileBase(BaseModel):
    # Core Fields
    startup_name: str = Field(
        ..., 
        max_length=150, 
        description="The name of the startup", 
        examples=["VentureTwin AI"]
    )
    startup_description: str = Field(
        ..., 
        description="Detailed description of the startup business", 
        examples=["An AI-powered digital twin platform for startups to simulate business scenarios."]
    )
    business_type: str = Field(
        ..., 
        max_length=100, 
        description="Type of business (e.g., SaaS, E-commerce, Manufacturing)", 
        examples=["SaaS"]
    )
    industry: str = Field(
        ..., 
        max_length=100, 
        description="Industry sector the startup operates in", 
        examples=["Artificial Intelligence"]
    )
    startup_stage: str = Field(
        ..., 
        max_length=100, 
        description="Current stage of the startup (e.g., Ideation, Seed, Series A)", 
        examples=["Seed"]
    )
    target_market: str = Field(
        ..., 
        max_length=150, 
        description="Target customer segment or market segment", 
        examples=["B2B Startups and SMBs"]
    )

    # Financial Fields
    initial_budget: Optional[float] = Field(
        default=0.0, 
        ge=0, 
        description="Initial budget allocated for the startup", 
        examples=[50000.0]
    )
    monthly_expenses: Optional[float] = Field(
        default=0.0, 
        ge=0, 
        description="Estimated monthly operating expenses", 
        examples=[8000.0]
    )
    expected_monthly_revenue: Optional[float] = Field(
        default=0.0, 
        ge=0, 
        description="Target monthly recurring revenue (MRR)", 
        examples=[15000.0]
    )
    funding_source: Optional[str] = Field(
        default=None, 
        max_length=100, 
        description="Primary source of funding (e.g., Bootstrapped, VC, Angel)", 
        examples=["Angel Round"]
    )

    # Team Fields
    founder_name: str = Field(
        ..., 
        max_length=100, 
        description="Name of the primary founder", 
        examples=["Jane Doe"]
    )
    has_cofounder: Optional[bool] = Field(
        default=False, 
        description="Indicates if the startup has co-founders", 
        examples=[True]
    )
    number_of_employees: Optional[int] = Field(
        default=0, 
        ge=0, 
        description="Total number of employees excluding founders", 
        examples=[5]
    )

    # Location Fields
    country: str = Field(
        ..., 
        max_length=100, 
        description="Country of operations", 
        examples=["United States"]
    )
    state: str = Field(
        ..., 
        max_length=100, 
        description="State or province of operations", 
        examples=["California"]
    )
    city: str = Field(
        ..., 
        max_length=100, 
        description="City of operations", 
        examples=["San Francisco"]
    )
    business_address: Optional[str] = Field(
        default=None, 
        description="Detailed street or office address", 
        examples=["100 Pine Street, Suite 1200"]
    )

    # Land/Facility Fields
    has_land: Optional[bool] = Field(
        default=False, 
        description="Indicates if the startup has physical land or office facility", 
        examples=[True]
    )
    land_status: Optional[str] = Field(
        default=None, 
        max_length=50, 
        description="Status of the land or office: 'renting', 'owned', or null", 
        examples=["renting"]
    )
    land_area_sqft: Optional[float] = Field(
        default=None, 
        ge=0, 
        description="Area of physical land or facility in square feet", 
        examples=[2500.0]
    )
    land_location: Optional[str] = Field(
        default=None, 
        max_length=150, 
        description="Geographic location of the land or facility", 
        examples=["Downtown Core"]
    )
    land_value: Optional[float] = Field(
        default=None, 
        ge=0, 
        description="Value of the land (applicable if owned)", 
        examples=[500000.0]
    )
    monthly_rent: Optional[float] = Field(
        default=None, 
        ge=0, 
        description="Monthly rent amount (applicable if renting)", 
        examples=[3500.0]
    )
    expandable: Optional[bool] = Field(
        default=None, 
        description="Indicates if physical land/facility can be expanded", 
        examples=[True]
    )


class CreateStartupProfile(StartupProfileBase):
    @model_validator(mode="after")
    def validate_land_rules(self) -> "CreateStartupProfile":
        # Land renting vs owning business rules validation
        status = self.land_status
        if status:
            status_lower = status.lower()
            if "rent" in status_lower:
                if self.monthly_rent is None or self.monthly_rent < 0:
                    raise ValueError("monthly_rent is required and must be >= 0 when land status is renting")
            elif "own" in status_lower:
                if self.monthly_rent is not None:
                    # Coerce monthly rent to None for owned land as per rule: "If owned land monthly_rent should be NULL"
                    self.monthly_rent = None
        else:
            # If no land status is set, monthly rent should be None
            self.monthly_rent = None
            
        return self


class UpdateStartupProfile(BaseModel):
    # Core Fields
    startup_name: Optional[str] = Field(default=None, max_length=150, description="The name of the startup")
    startup_description: Optional[str] = Field(default=None, description="Detailed description of the startup business")
    business_type: Optional[str] = Field(default=None, max_length=100, description="Type of business")
    industry: Optional[str] = Field(default=None, max_length=100, description="Industry sector")
    startup_stage: Optional[str] = Field(default=None, max_length=100, description="Current stage of the startup")
    target_market: Optional[str] = Field(default=None, max_length=150, description="Target customer segment")

    # Financial Fields
    initial_budget: Optional[float] = Field(default=None, ge=0)
    monthly_expenses: Optional[float] = Field(default=None, ge=0)
    expected_monthly_revenue: Optional[float] = Field(default=None, ge=0)
    funding_source: Optional[str] = Field(default=None, max_length=100)

    # Team Fields
    founder_name: Optional[str] = Field(default=None, max_length=100)
    has_cofounder: Optional[bool] = Field(default=None)
    number_of_employees: Optional[int] = Field(default=None, ge=0)

    # Location Fields
    country: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    business_address: Optional[str] = Field(default=None)

    # Land Fields
    has_land: Optional[bool] = Field(default=None)
    land_status: Optional[str] = Field(default=None, max_length=50)
    land_area_sqft: Optional[float] = Field(default=None, ge=0)
    land_location: Optional[str] = Field(default=None, max_length=150)
    land_value: Optional[float] = Field(default=None, ge=0)
    monthly_rent: Optional[float] = Field(default=None, ge=0)
    expandable: Optional[bool] = Field(default=None)

    @model_validator(mode="after")
    def validate_land_rules(self) -> "UpdateStartupProfile":
        status = self.land_status
        if status:
            status_lower = status.lower()
            if "rent" in status_lower:
                if self.monthly_rent is None:
                    # Only raise error if monthly_rent is not provided or set to None
                    raise ValueError("monthly_rent is required when land status is renting")
            elif "own" in status_lower:
                self.monthly_rent = None
        return self


class StartupProfileResponse(StartupProfileBase):
    startup_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

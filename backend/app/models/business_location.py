# app/models/business_location.py
# Re-export BusinessLocation from startup_profile to maintain a single source of truth.
# The model is defined in startup_profile.py alongside its parent (StartupProfile)
# to allow SQLAlchemy to resolve all relationships at import time without circular imports.

from app.models.startup_profile import BusinessLocation

__all__ = ["BusinessLocation"]

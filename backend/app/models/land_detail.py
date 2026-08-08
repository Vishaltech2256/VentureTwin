# app/models/land_detail.py
# Re-export LandDetail from startup_profile to maintain a single source of truth.
# The model is defined in startup_profile.py alongside its parent (StartupProfile)
# to allow SQLAlchemy to resolve all relationships at import time without circular imports.

from app.models.startup_profile import LandDetail

__all__ = ["LandDetail"]

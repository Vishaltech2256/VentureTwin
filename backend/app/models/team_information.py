# app/models/team_information.py
# Re-exports TeamInformation from startup_profile.py to maintain a single source of truth.
# The model is defined in startup_profile.py alongside its parent (StartupProfile)
# so SQLAlchemy can resolve all back-references at import time without circular imports.

from app.models.startup_profile import TeamInformation

__all__ = ["TeamInformation"]

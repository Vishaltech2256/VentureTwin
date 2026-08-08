"""Compatibility export used by Alembic migrations."""

from app.database.database import Base

# Import ORM models so Alembic autogenerate sees their table metadata.
from app.models.ai_suggestion import AISuggestion
from app.models.prediction import Prediction
from app.models.report import Report
from app.models.startup_profile import StartupProfile
from app.models.user import User

__all__ = ["Base"]

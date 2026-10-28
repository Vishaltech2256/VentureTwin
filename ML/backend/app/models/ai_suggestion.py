"""Persistence model for AI-generated startup recommendations."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.prediction import Prediction
    from app.models.startup_profile import StartupProfile


class AISuggestion(Base):
    """A recommendation generated from a startup prediction."""

    __tablename__ = "ai_suggestions"
    __table_args__ = (
        CheckConstraint(
            "priority IN ('HIGH', 'MEDIUM', 'LOW')",
            name="ck_ai_suggestions_priority",
        ),
        CheckConstraint(
            "category IN ('Finance', 'Marketing', 'Operations', 'Hiring', "
            "'Growth', 'Investment')",
            name="ck_ai_suggestions_category",
        ),
    )

    suggestion_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    startup_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("startup_profiles.startup_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prediction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("predictions.prediction_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(10), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    startup: Mapped["StartupProfile"] = relationship(
        "StartupProfile", backref="ai_suggestions"
    )
    prediction: Mapped["Prediction"] = relationship(
        "Prediction", backref="ai_suggestions"
    )


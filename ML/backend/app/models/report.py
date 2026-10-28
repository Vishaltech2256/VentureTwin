"""SQLAlchemy model for persisted startup report metadata."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Report(Base):
    """A generated business report for a single startup."""

    __tablename__ = "reports"

    report_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    startup_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("startup_profiles.startup_id", ondelete="CASCADE"),
        nullable=False,
    )
    report_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    report_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generated_on: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    startup: Mapped["StartupProfile"] = relationship(
        "StartupProfile", backref="reports"
    )

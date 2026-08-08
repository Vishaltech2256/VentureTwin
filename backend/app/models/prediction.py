# app/models/prediction.py

from datetime import datetime, timezone
from sqlalchemy import Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    startup_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("startup_profiles.startup_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    revenue_prediction: Mapped[float] = mapped_column(
        Numeric(15, 2), nullable=False
    )
    profit_prediction: Mapped[float] = mapped_column(
        Numeric(15, 2), nullable=False
    )
    risk_level: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    health_score: Mapped[float] = mapped_column(
        Numeric(5, 2), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationship back to the parent startup
    startup = relationship("StartupProfile", backref="predictions")


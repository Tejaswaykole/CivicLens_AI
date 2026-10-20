"""Storage for a future model. This phase does not insert predictions."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import ComplaintPriority
from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.types import pg_enum

if TYPE_CHECKING:
    from app.models.complaint import Complaint


class ModelPrediction(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "model_predictions"
    __table_args__ = (
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="confidence_range",
        ),
        Index("ix_model_predictions_complaint_id", "complaint_id"),
        Index("ix_model_predictions_predicted_at", "predicted_at"),
    )

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("complaints.id", ondelete="RESTRICT"),
        nullable=False,
    )
    model_identifier: Mapped[str] = mapped_column(String(200), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    predicted_category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    suggested_priority: Mapped[ComplaintPriority | None] = mapped_column(
        pg_enum(ComplaintPriority, "complaint_priority"),
        nullable=True,
    )
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    explanation: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    predicted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    complaint: Mapped["Complaint"] = relationship(back_populates="predictions")

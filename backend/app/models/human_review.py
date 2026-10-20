"""Human priority decisions. Machine suggestions stay on model_predictions."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import ComplaintPriority, SuggestionOrigin
from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.types import pg_enum

if TYPE_CHECKING:
    from app.models.complaint import Complaint
    from app.models.user import User


class HumanReview(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "human_reviews"
    __table_args__ = (
        CheckConstraint(
            "suggested_priority IS NULL "
            "OR suggested_priority = confirmed_priority "
            "OR (justification IS NOT NULL AND char_length(btrim(justification)) >= 10)",
            name="override_justification",
        ),
        Index("ix_human_reviews_complaint_id", "complaint_id"),
        Index("ix_human_reviews_reviewer_user_id", "reviewer_user_id"),
        Index("ix_human_reviews_reviewed_at", "reviewed_at"),
    )

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("complaints.id", ondelete="RESTRICT"),
        nullable=False,
    )
    reviewer_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    suggested_priority: Mapped[ComplaintPriority | None] = mapped_column(
        pg_enum(ComplaintPriority, "complaint_priority"),
        nullable=True,
    )
    confirmed_priority: Mapped[ComplaintPriority] = mapped_column(
        pg_enum(ComplaintPriority, "complaint_priority"),
        nullable=False,
    )
    suggestion_origin: Mapped[SuggestionOrigin] = mapped_column(
        pg_enum(SuggestionOrigin, "suggestion_origin"),
        nullable=False,
    )
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    complaint: Mapped["Complaint"] = relationship(back_populates="reviews")
    reviewer: Mapped["User"] = relationship()

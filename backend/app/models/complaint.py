"""Citizen complaints. The public reference is separate from the UUID primary key."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import ComplaintStatus
from app.domain.workflow import COMPLAINT_CATEGORIES
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.types import pg_enum

if TYPE_CHECKING:
    from app.models.assignment import ComplaintAssignment
    from app.models.complaint_status_history import ComplaintStatusHistory
    from app.models.department import Department
    from app.models.human_review import HumanReview
    from app.models.model_prediction import ModelPrediction
    from app.models.user import User

_CATEGORY_LIST = ", ".join(f"'{category}'" for category in COMPLAINT_CATEGORIES)


class Complaint(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "complaints"
    __table_args__ = (
        CheckConstraint(
            f"category IN ({_CATEGORY_LIST})",
            name="known_category",
        ),
        CheckConstraint(
            "public_reference ~ '^DEL-[0-9]{4}-[0-9]{6}$'",
            name="public_reference_format",
        ),
        CheckConstraint("char_length(btrim(title)) >= 3", name="title_present"),
        CheckConstraint("char_length(btrim(description)) >= 10", name="description_present"),
        CheckConstraint(
            "char_length(btrim(location_address)) >= 3",
            name="location_present",
        ),
        Index("ix_complaints_citizen_id", "citizen_id"),
        Index("ix_complaints_status", "status"),
        Index("ix_complaints_department_id", "department_id"),
        Index("ix_complaints_category", "category"),
        Index("ix_complaints_created_at", "created_at"),
    )

    public_reference: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    citizen_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    ward_zone: Mapped[str | None] = mapped_column(String(200), nullable=True)
    location_address: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[ComplaintStatus] = mapped_column(
        pg_enum(ComplaintStatus, "complaint_status"),
        nullable=False,
        default=ComplaintStatus.submitted,
        server_default=text("'submitted'::complaint_status"),
    )
    requested_department_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=True,
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=True,
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    citizen: Mapped["User"] = relationship(foreign_keys=[citizen_id])
    requested_department: Mapped["Department | None"] = relationship(
        foreign_keys=[requested_department_id],
        back_populates="requested_complaints",
    )
    department: Mapped["Department | None"] = relationship(
        foreign_keys=[department_id],
        back_populates="assigned_complaints",
    )
    assignments: Mapped[list["ComplaintAssignment"]] = relationship(
        back_populates="complaint",
        order_by="ComplaintAssignment.assigned_at",
    )
    status_history: Mapped[list["ComplaintStatusHistory"]] = relationship(
        back_populates="complaint",
        order_by="ComplaintStatusHistory.created_at",
    )
    predictions: Mapped[list["ModelPrediction"]] = relationship(
        back_populates="complaint",
        order_by="ModelPrediction.predicted_at",
    )
    reviews: Mapped[list["HumanReview"]] = relationship(
        back_populates="complaint",
        order_by="HumanReview.reviewed_at",
    )

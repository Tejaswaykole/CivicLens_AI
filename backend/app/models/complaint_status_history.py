"""Status changes. The actor id is a recorded identifier, not proof of authentication."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import ComplaintStatus
from app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin
from app.models.types import pg_enum

if TYPE_CHECKING:
    from app.models.complaint import Complaint
    from app.models.user import User


class ComplaintStatusHistory(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "complaint_status_history"
    __table_args__ = (
        CheckConstraint(
            "previous_status IS NULL OR previous_status <> new_status",
            name="status_actually_changed",
        ),
        Index("ix_complaint_status_history_complaint_id", "complaint_id"),
        Index("ix_complaint_status_history_created_at", "created_at"),
    )

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("complaints.id", ondelete="RESTRICT"),
        nullable=False,
    )
    previous_status: Mapped[ComplaintStatus | None] = mapped_column(
        pg_enum(ComplaintStatus, "complaint_status"),
        nullable=True,
    )
    new_status: Mapped[ComplaintStatus] = mapped_column(
        pg_enum(ComplaintStatus, "complaint_status"),
        nullable=False,
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    actor_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    complaint: Mapped["Complaint"] = relationship(back_populates="status_history")
    actor: Mapped["User | None"] = relationship()

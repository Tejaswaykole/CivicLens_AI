"""Assignment history. A partial unique index allows one current assignment per complaint."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.complaint import Complaint
    from app.models.department import Department
    from app.models.user import User


class ComplaintAssignment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "complaint_assignments"
    __table_args__ = (
        Index("ix_complaint_assignments_complaint_id", "complaint_id"),
        Index("ix_complaint_assignments_department_id", "department_id"),
        Index("ix_complaint_assignments_officer_id", "assigned_officer_id"),
        Index(
            "uq_complaint_assignments_one_current",
            "complaint_id",
            unique=True,
            postgresql_where=text("is_current"),
        ),
    )

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("complaints.id", ondelete="RESTRICT"),
        nullable=False,
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
    )
    assigned_officer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    assigned_crew_unit: Mapped[str | None] = mapped_column(String(200), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    complaint: Mapped["Complaint"] = relationship(back_populates="assignments")
    department: Mapped["Department"] = relationship()
    assigned_officer: Mapped["User | None"] = relationship()

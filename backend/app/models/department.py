"""Line agencies shown in the frontend department administration screen."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.complaint import Complaint
    from app.models.user import User


class Department(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "departments"
    __table_args__ = (
        CheckConstraint("sla_target_hours > 0", name="sla_positive"),
        Index("ix_departments_is_active", "is_active"),
    )

    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    nodal_officer_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    sla_target_hours: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    users: Mapped[list["User"]] = relationship(back_populates="department")
    requested_complaints: Mapped[list["Complaint"]] = relationship(
        back_populates="requested_department",
        foreign_keys="Complaint.requested_department_id",
    )
    assigned_complaints: Mapped[list["Complaint"]] = relationship(
        back_populates="department",
        foreign_keys="Complaint.department_id",
    )

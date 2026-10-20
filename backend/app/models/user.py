"""Accounts. Password hashes are stored for a later authentication phase and never returned."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import UserRole
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.types import pg_enum

if TYPE_CHECKING:
    from app.models.department import Department


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_role", "role"),
        Index("ix_users_department_id", "department_id"),
        Index("ix_users_is_active", "is_active"),
    )

    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(pg_enum(UserRole, "user_role"), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=True,
    )
    designation: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ward_or_zone: Mapped[str | None] = mapped_column(String(200), nullable=True)

    department: Mapped["Department | None"] = relationship(back_populates="users")

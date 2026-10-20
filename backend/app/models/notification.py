"""In-app notifications addressed to a user, a role, or both."""

import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import NotificationType, UserRole
from app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin
from app.models.types import pg_enum
from app.models.user import User


class Notification(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint(
            "recipient_user_id IS NOT NULL OR recipient_role IS NOT NULL",
            name="has_recipient",
        ),
        Index("ix_notifications_recipient_user_id", "recipient_user_id"),
        Index("ix_notifications_recipient_role", "recipient_role"),
        Index("ix_notifications_is_read", "is_read"),
        Index("ix_notifications_created_at", "created_at"),
    )

    recipient_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    recipient_role: Mapped[UserRole | None] = mapped_column(
        pg_enum(UserRole, "user_role"),
        nullable=True,
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        pg_enum(NotificationType, "notification_type"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    link: Mapped[str | None] = mapped_column(String(300), nullable=True)
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    recipient: Mapped[User | None] = relationship()

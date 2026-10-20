"""Notification responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import NotificationType, UserRole


class NotificationRead(BaseModel):
    id: uuid.UUID
    recipient_user_id: uuid.UUID | None
    recipient_role: UserRole | None
    notification_type: NotificationType
    title: str
    message: str
    link: str | None
    is_read: bool
    created_at: datetime

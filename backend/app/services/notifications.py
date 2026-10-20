"""Create and read notifications for real application events."""

import uuid

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.domain.enums import NotificationType, UserRole
from app.models.notification import Notification
from app.repositories.notifications import get_notification, list_notifications
from app.schemas.common import Page, PageParams
from app.schemas.mappers import notification_to_read
from app.schemas.notification import NotificationRead


def _safe_link(link: str | None) -> str | None:
    if link is None:
        return None
    if not link.startswith("/") or link.startswith("//") or "\\" in link:
        raise AppError("invalid_link", "Notification links must be relative paths.", 422)
    return link


def notify(
    db: Session,
    *,
    title: str,
    message: str,
    notification_type: NotificationType,
    recipient_user_id: uuid.UUID | None = None,
    recipient_role: UserRole | None = None,
    link: str | None = None,
) -> None:
    if recipient_user_id is None and recipient_role is None:
        raise AppError("invalid_notification", "A notification needs a recipient.", 422)
    db.add(
        Notification(
            recipient_user_id=recipient_user_id,
            recipient_role=recipient_role,
            notification_type=notification_type,
            title=title[:200],
            message=message[:500],
            link=_safe_link(link),
        )
    )


def list_for_filters(
    db: Session,
    params: PageParams,
    *,
    recipient_user_id: uuid.UUID | None,
    recipient_role: UserRole | None,
    is_read: bool | None,
) -> Page[NotificationRead]:
    rows, total = list_notifications(
        db,
        params,
        recipient_user_id=recipient_user_id,
        recipient_role=recipient_role,
        is_read=is_read,
    )
    return Page(
        items=[notification_to_read(row) for row in rows],
        page=params.page,
        page_size=params.page_size,
        total=total,
    )


def mark_read(db: Session, notification_id: uuid.UUID) -> NotificationRead:
    notification = get_notification(db, notification_id)
    if notification is None:
        raise AppError("not_found", "Notification not found.", 404)
    notification.is_read = True
    db.flush()
    return notification_to_read(notification)

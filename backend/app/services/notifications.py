"""Create and read notifications for real application events."""

import uuid

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.domain.enums import NotificationType, UserRole
from app.models.notification import Notification
from app.models.user import User
from app.repositories.notifications import (
    get_notification,
    list_notifications,
    list_visible_notifications,
)
from app.schemas.common import Page, PageParams
from app.schemas.mappers import notification_to_read
from app.schemas.notification import NotificationRead
from app.services.authorization import forbid


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


def list_for_viewer(
    db: Session,
    params: PageParams,
    viewer: User,
    *,
    recipient_user_id: uuid.UUID | None,
    recipient_role: UserRole | None,
    is_read: bool | None,
) -> Page[NotificationRead]:
    if viewer.role == UserRole.system_admin:
        rows, total = list_notifications(
            db,
            params,
            recipient_user_id=recipient_user_id,
            recipient_role=recipient_role,
            is_read=is_read,
        )
    else:
        if recipient_user_id is not None and recipient_user_id != viewer.id:
            raise forbid("You can only read your own notifications.")
        if recipient_role is not None and recipient_role != viewer.role:
            raise forbid("You can only read notifications for your own role.")
        rows, total = list_visible_notifications(
            db,
            params,
            viewer_id=viewer.id,
            viewer_role=viewer.role,
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


def _can_see(viewer: User, notification: Notification) -> bool:
    if viewer.role == UserRole.system_admin:
        return True
    if notification.recipient_user_id == viewer.id:
        return True
    return (
        notification.recipient_user_id is None and notification.recipient_role == viewer.role
    )


def mark_read(db: Session, notification_id: uuid.UUID, viewer: User) -> NotificationRead:
    notification = get_notification(db, notification_id)
    if notification is None or not _can_see(viewer, notification):
        raise AppError("not_found", "Notification not found.", 404)
    notification.is_read = True
    db.flush()
    return notification_to_read(notification)

"""Notification queries."""

import uuid

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.domain.enums import UserRole
from app.models.notification import Notification
from app.schemas.common import PageParams


def list_notifications(
    db: Session,
    params: PageParams,
    *,
    recipient_user_id: uuid.UUID | None,
    recipient_role: UserRole | None,
    is_read: bool | None,
) -> tuple[list[Notification], int]:
    criteria = []
    if recipient_user_id is not None:
        criteria.append(Notification.recipient_user_id == recipient_user_id)
    if recipient_role is not None:
        criteria.append(Notification.recipient_role == recipient_role)
    if is_read is not None:
        criteria.append(Notification.is_read == is_read)
    stmt = select(Notification).where(*criteria)
    total = db.scalar(select(func.count()).select_from(Notification).where(*criteria)) or 0
    rows = db.scalars(
        stmt.order_by(Notification.created_at.desc()).offset(params.offset).limit(params.page_size)
    )
    return list(rows), int(total)


def visibility_clause(viewer_id: uuid.UUID, viewer_role: UserRole):
    return or_(
        Notification.recipient_user_id == viewer_id,
        and_(
            Notification.recipient_user_id.is_(None),
            Notification.recipient_role == viewer_role,
        ),
    )


def list_visible_notifications(
    db: Session,
    params: PageParams,
    *,
    viewer_id: uuid.UUID,
    viewer_role: UserRole,
    recipient_user_id: uuid.UUID | None,
    recipient_role: UserRole | None,
    is_read: bool | None,
) -> tuple[list[Notification], int]:
    criteria = [visibility_clause(viewer_id, viewer_role)]
    if recipient_user_id is not None:
        criteria.append(Notification.recipient_user_id == recipient_user_id)
    if recipient_role is not None:
        criteria.append(Notification.recipient_role == recipient_role)
    if is_read is not None:
        criteria.append(Notification.is_read == is_read)
    stmt = select(Notification).where(*criteria)
    total = db.scalar(select(func.count()).select_from(Notification).where(*criteria)) or 0
    rows = db.scalars(
        stmt.order_by(Notification.created_at.desc()).offset(params.offset).limit(params.page_size)
    )
    return list(rows), int(total)


def get_notification(db: Session, notification_id: uuid.UUID) -> Notification | None:
    return db.get(Notification, notification_id)

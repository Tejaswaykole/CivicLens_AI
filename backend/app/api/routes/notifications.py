"""Notification reads and read-state updates."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import pagination_params
from app.core.database import get_db
from app.domain.enums import UserRole
from app.schemas.common import Page, PageParams
from app.schemas.notification import NotificationRead
from app.services import notifications as notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=Page[NotificationRead])
def list_notifications(
    recipient_user_id: uuid.UUID | None = None,
    recipient_role: UserRole | None = None,
    is_read: bool | None = None,
    params: PageParams = Depends(pagination_params),
    db: Session = Depends(get_db),
) -> Page[NotificationRead]:
    return notification_service.list_for_filters(
        db,
        params,
        recipient_user_id=recipient_user_id,
        recipient_role=recipient_role,
        is_read=is_read,
    )


@router.patch("/{notification_id}/read", response_model=NotificationRead)
def mark_notification_read(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> NotificationRead:
    return notification_service.mark_read(db, notification_id)
